<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Support\Str;

class Classroom extends Model
{
    protected $fillable = ['teacher_id', 'name', 'subject', 'code'];

    // ── Relationships ──────────────────────────────────────────────────────

    public function teacher(): BelongsTo
    {
        return $this->belongsTo(User::class, 'teacher_id');
    }

    public function students(): BelongsToMany
    {
        return $this->belongsToMany(User::class, 'classroom_student', 'classroom_id', 'user_id')
                    ->withPivot('joined_at')
                    ->withTimestamps();
    }

    public function notifications(): HasMany
    {
        return $this->hasMany(ClassroomNotification::class)->latest();
    }

    // ── Helper: generate a unique 6-char alphanumeric code ─────────────────

    public static function generateUniqueCode(): string
    {
        do {
            $code = strtoupper(Str::random(6));
        } while (self::where('code', $code)->exists());

        return $code;
    }
}
