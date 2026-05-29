<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return view('welcome');
});

// API endpoint to get GROQ API key for chatbot - no database required
Route::get('/api/groq-key', function () {
    return response()->json([
        'key' => env('VITE_GROQ_API_KEY', ''),
    ])->header('Cache-Control', 'no-cache');
})->withoutMiddleware(['Illuminate\Foundation\Http\Middleware\VerifyCsrfToken']);
