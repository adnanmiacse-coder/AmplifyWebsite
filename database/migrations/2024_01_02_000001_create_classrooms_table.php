<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // ── classrooms ────────────────────────────────────────────────────────
        Schema::create('classrooms', function (Blueprint $table) {
            $table->id();
            $table->foreignId('teacher_id')->constrained('users')->onDelete('cascade');
            $table->string('name');
            $table->string('subject')->nullable();
            $table->string('code', 8)->unique(); // random e.g. "ABC123XY"
            $table->timestamps();
        });

        // ── classroom_student  (many-to-many pivot) ───────────────────────────
        Schema::create('classroom_student', function (Blueprint $table) {
            $table->id();
            $table->foreignId('classroom_id')->constrained()->onDelete('cascade');
            $table->foreignId('user_id')->constrained()->onDelete('cascade');
            $table->timestamp('joined_at')->useCurrent();
            $table->unique(['classroom_id', 'user_id']); // prevent duplicate joins
        });

        // ── classroom_notifications ───────────────────────────────────────────
        Schema::create('classroom_notifications', function (Blueprint $table) {
            $table->id();
            $table->foreignId('classroom_id')->constrained()->onDelete('cascade');
            $table->text('message');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('classroom_notifications');
        Schema::dropIfExists('classroom_student');
        Schema::dropIfExists('classrooms');
    }
};
