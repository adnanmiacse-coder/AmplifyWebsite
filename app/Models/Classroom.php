<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Support\Str;

class Classroom extends Model
{
    use HasFactory;

    protected $fillable = [
        'teacher_id',
        'name',
        'subject',
        'code',
    ];

    public function teacher(): BelongsTo
    {
        return $this->belongsTo(User::class, 'teacher_id');
    }

    public function students(): BelongsToMany
    {
        return $this->belongsToMany(User::class, 'classroom_student', 'classroom_id', 'user_id')
            ->withPivot('joined_at')
            ;
    }

    public function notifications(): HasMany
    {
        return $this->hasMany(ClassroomNotification::class);
    }

    public static function generateUniqueCode(int $length = 8): string
    {
        $length = max(4, min(12, $length));

        do {
            // Uppercase alphanumeric, avoid confusing chars.
            $code = Str::upper(Str::random($length));
            $code = str_replace(['O', '0', 'I', '1', 'L'], ['P', '2', 'J', '3', 'M'], $code);
        } while (self::where('code', $code)->exists());

        return $code;
    }
}

