<?php

namespace App\Http\Controllers;

use App\Models\Classroom;
use App\Models\ClassroomNotification;
use Illuminate\Http\Request;

class ClassroomController extends Controller
{
    // ─────────────────────────────────────────────────────────────────────
    // POST /api/classrooms
    // Teacher creates a new classroom. Returns generated join code.
    // Body: { name, subject? }
    // ─────────────────────────────────────────────────────────────────────
    public function create(Request $request)
    {
        $this->requireRole($request, 'teacher');

        $validated = $request->validate([
            'name'    => ['required', 'string', 'max:255'],
            'subject' => ['nullable', 'string', 'max:255'],
        ]);

        $classroom = Classroom::create([
            'teacher_id' => $request->user()->id,
            'name'       => $validated['name'],
            'subject'    => $validated['subject'] ?? null,
            'code'       => Classroom::generateUniqueCode(),
        ]);

        return response()->json([
            'message'   => 'Classroom created.',
            'classroom' => $this->formatClassroom($classroom),
        ], 201);
    }

    // ─────────────────────────────────────────────────────────────────────
    // GET /api/classrooms
    // Teacher: list their own classrooms.
    // Student: list classrooms they have joined.
    // ─────────────────────────────────────────────────────────────────────
    public function index(Request $request)
    {
        $user = $request->user();

        if ($user->role === 'teacher') {
            $classrooms = Classroom::where('teacher_id', $user->id)
                ->withCount('students')
                ->get()
                ->map(fn($c) => $this->formatClassroom($c));
        } else {
            $classrooms = $user->classrooms()
                ->withCount('students')
                ->get()
                ->map(fn($c) => $this->formatClassroom($c, withTeacher: true));
        }

        return response()->json(['classrooms' => $classrooms]);
    }

    // ─────────────────────────────────────────────────────────────────────
    // POST /api/classrooms/join
    // Student joins a classroom using a code.
    // Body: { code }
    // ─────────────────────────────────────────────────────────────────────
    public function join(Request $request)
    {
        $this->requireRole($request, 'student');

        $request->validate([
            'code' => ['required', 'string'],
        ]);

        $classroom = Classroom::where('code', strtoupper(trim($request->code)))->first();

        if (! $classroom) {
            return response()->json(['message' => 'Invalid classroom code.'], 404);
        }

        $user = $request->user();

        // Already a member?
        if ($classroom->students()->where('user_id', $user->id)->exists()) {
            return response()->json(['message' => 'You have already joined this classroom.'], 409);
        }

        $classroom->students()->attach($user->id, ['joined_at' => now()]);

        return response()->json([
            'message'   => 'Joined classroom successfully.',
            'classroom' => $this->formatClassroom($classroom, withTeacher: true),
        ]);
    }

    // ─────────────────────────────────────────────────────────────────────
    // GET /api/classrooms/{id}
    // Dashboard for a specific classroom.
    // Teacher sees student list + notifications.
    // Student sees class info + notifications (must be a member).
    // ─────────────────────────────────────────────────────────────────────
    public function show(Request $request, int $id)
    {
        $classroom = Classroom::with(['teacher', 'notifications'])->findOrFail($id);
        $user      = $request->user();

        if ($user->role === 'teacher') {
            // Must own this classroom
            if ($classroom->teacher_id !== $user->id) {
                return response()->json(['message' => 'Forbidden.'], 403);
            }
            $students = $classroom->students()->get()->map(fn($s) => [
                'id'        => $s->id,
                'name'      => $s->name,
                'email'     => $s->email,
                'joined_at' => $s->pivot->joined_at,
            ]);
        } else {
            // Must be a member
            if (! $classroom->students()->where('user_id', $user->id)->exists()) {
                return response()->json(['message' => 'You are not a member of this classroom.'], 403);
            }
            $students = null;
        }

        return response()->json([
            'classroom'     => $this->formatClassroom($classroom, withTeacher: true),
            'notifications' => $classroom->notifications->map(fn($n) => [
                'id'         => $n->id,
                'message'    => $n->message,
                'created_at' => $n->created_at,
            ]),
            'students' => $students, // null for students, array for teachers
        ]);
    }

    // ─────────────────────────────────────────────────────────────────────
    // POST /api/classrooms/{id}/notify
    // Teacher sends a notification to all students in the classroom.
    // Body: { message }
    // ─────────────────────────────────────────────────────────────────────
    public function notify(Request $request, int $id)
    {
        $this->requireRole($request, 'teacher');

        $classroom = Classroom::findOrFail($id);

        if ($classroom->teacher_id !== $request->user()->id) {
            return response()->json(['message' => 'Forbidden.'], 403);
        }

        $request->validate([
            'message' => ['required', 'string', 'max:2000'],
        ]);

        $notification = ClassroomNotification::create([
            'classroom_id' => $classroom->id,
            'message'      => $request->message,
        ]);

        return response()->json([
            'message'      => 'Notification sent.',
            'notification' => [
                'id'         => $notification->id,
                'message'    => $notification->message,
                'created_at' => $notification->created_at,
            ],
        ], 201);
    }

    // ─────────────────────────────────────────────────────────────────────
    // DELETE /api/classrooms/{id}/leave
    // Student leaves a classroom.
    // ─────────────────────────────────────────────────────────────────────
    public function leave(Request $request, int $id)
    {
        $this->requireRole($request, 'student');

        $classroom = Classroom::findOrFail($id);
        $user      = $request->user();

        if (! $classroom->students()->where('user_id', $user->id)->exists()) {
            return response()->json(['message' => 'You are not in this classroom.'], 409);
        }

        $classroom->students()->detach($user->id);

        return response()->json(['message' => 'Left classroom successfully.']);
    }

    // ─────────────────────────────────────────────────────────────────────
    // DELETE /api/classrooms/{id}
    // Teacher deletes their classroom.
    // ─────────────────────────────────────────────────────────────────────
    public function destroy(Request $request, int $id)
    {
        $this->requireRole($request, 'teacher');

        $classroom = Classroom::findOrFail($id);

        if ($classroom->teacher_id !== $request->user()->id) {
            return response()->json(['message' => 'Forbidden.'], 403);
        }

        $classroom->delete();

        return response()->json(['message' => 'Classroom deleted.']);
    }

    // ─────────────────────────────────────────────────────────────────────
    // Helpers
    // ─────────────────────────────────────────────────────────────────────

    private function requireRole(Request $request, string $role): void
    {
        if ($request->user()->role !== $role) {
            abort(403, "Only {$role}s can perform this action.");
        }
    }

    private function formatClassroom(Classroom $c, bool $withTeacher = false): array
    {
        $data = [
            'id'             => $c->id,
            'name'           => $c->name,
            'subject'        => $c->subject,
            'code'           => $c->code,
            'student_count'  => $c->students_count ?? $c->students()->count(),
            'created_at'     => $c->created_at,
        ];

        if ($withTeacher && $c->relationLoaded('teacher')) {
            $data['teacher'] = [
                'id'   => $c->teacher->id,
                'name' => $c->teacher->name,
            ];
        }

        return $data;
    }
}
