<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\ClassroomController;
use Illuminate\Support\Facades\Route;

// ── Public auth routes ────────────────────────────────────────────────────────
Route::post('/register', [AuthController::class, 'register']);
Route::post('/login',    [AuthController::class, 'login']);

// ── Protected routes (Sanctum token required) ─────────────────────────────────
Route::middleware('auth:sanctum')->group(function () {

    // Auth
    Route::get('/user',    [AuthController::class, 'user']);
    Route::post('/logout', [AuthController::class, 'logout']);

    // ── Classroom routes ──────────────────────────────────────────────────────

    // Teacher: create classroom
    Route::post('/classrooms',              [ClassroomController::class, 'create']);

    // Both: list own classrooms (teacher → owned, student → joined)
    Route::get('/classrooms',               [ClassroomController::class, 'index']);

    // Student: join via code
    Route::post('/classrooms/join',         [ClassroomController::class, 'join']);

    // Both: view classroom dashboard
    Route::get('/classrooms/{id}',          [ClassroomController::class, 'show']);

    // Teacher: send notification to classroom
    Route::post('/classrooms/{id}/notify',  [ClassroomController::class, 'notify']);

    // Student: leave a classroom
    Route::delete('/classrooms/{id}/leave', [ClassroomController::class, 'leave']);

    // Teacher: delete classroom
    Route::delete('/classrooms/{id}',       [ClassroomController::class, 'destroy']);
});