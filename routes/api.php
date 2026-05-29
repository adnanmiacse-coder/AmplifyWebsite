<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\ClassroomController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Route;

// ── Public API config endpoint ────────────────────────────────────────────────
Route::get('/config', function (Request $request) {
    // Serve API keys and configuration from server, not from client bundle
    // This way keys are never exposed in the front-end code
    return response()->json([
        'GROQ_API_KEY'        => env('GROQ_API_KEY', ''),
        'GROQ_API_BASE_URL'   => env('GROQ_API_BASE_URL', 'https://api.groq.com/openai/v1'),
        'CEREBRAS_API_KEY'    => env('CEREBRAS_API_KEY', ''),
        'CEREBRAS_API_BASE'   => env('CEREBRAS_API_BASE_URL', 'https://api.cerebras.ai/v1'),
        'OPENROUTER_KEYS'     => explode(',', env('OPENROUTER_KEYS', '')),
        'OPENROUTER_BASE'     => env('OPENROUTER_BASE', 'https://openrouter.ai/api/v1'),
        'GEMINI_KEY'          => env('GEMINI_API_KEY', ''),
        'GEMINI_MODEL'        => env('GEMINI_MODEL', 'gemini-2.0-flash-lite'),
        'GEMINI_BASE'         => env('GEMINI_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta/models'),
    ]);
});

// ── Public auth routes ────────────────────────────────────────────────────────
Route::post('/register', [AuthController::class, 'register']);
Route::post('/login',    [AuthController::class, 'login']);

Route::get('/opportunities', function (Request $request) {
    $sources = [
        ['url' => 'https://opportunitydesk.org/feed/', 'label' => 'Opportunity Desk', 'type' => 'Scholarship'],
        ['url' => 'https://www.scholars4dev.com/feed/', 'label' => 'Scholars4Dev', 'type' => 'Scholarship'],
        ['url' => 'https://afterschoolafrica.com/feed/', 'label' => 'After School Africa', 'type' => 'Fellowship'],
        ['url' => 'https://www.findaphd.com/rss/scholarships.aspx', 'label' => 'FindAPhD', 'type' => 'Research'],
    ];

    $items = [];

    $guessType = function (string $title, string $sourceType) {
        $text = strtolower($title);
        if (str_contains($text, 'research') || str_contains($text, 'phd') || str_contains($text, 'postdoc')) {
            return 'Research';
        }
        if (str_contains($text, 'fellowship') || str_contains($text, 'fellow')) {
            return 'Fellowship';
        }
        if (str_contains($text, 'scholarship') || str_contains($text, 'grant') || str_contains($text, 'award')) {
            return 'Scholarship';
        }
        return $sourceType;
    };

    $guessRegion = function (string $title, ?string $desc = null) {
        $text = strtolower($title . ' ' . ($desc ?? ''));
        if (str_contains($text, 'usa') || str_contains($text, 'united states') || str_contains($text, 'america')) {
            return '🇺🇸 USA';
        }
        if (str_contains($text, 'uk') || str_contains($text, 'united kingdom') || str_contains($text, 'britain') || str_contains($text, 'england')) {
            return '🇬🇧 UK';
        }
        if (str_contains($text, 'europe') || str_contains($text, 'germany') || str_contains($text, 'france') || str_contains($text, 'eu ')) {
            return '🇪🇺 EU';
        }
        if (str_contains($text, 'japan')) {
            return '🇯🇵 Japan';
        }
        if (str_contains($text, 'korea')) {
            return '🇰🇷 Korea';
        }
        if (str_contains($text, 'canada')) {
            return '🇨🇦 Canada';
        }
        if (str_contains($text, 'australia')) {
            return '🇦🇺 Australia';
        }
        return '🌍 International';
    };

    $fallback = [
        ['title' => 'Chevening Scholarships 2025', 'desc' => 'UK government scholarship for future leaders. Full funding for one-year masters degree at any UK university.', 'link' => 'https://www.chevening.org', 'source' => 'Chevening', 'type' => 'Scholarship', 'region' => '🇬🇧 UK', 'date' => ''],
        ['title' => 'Fulbright Foreign Student Program', 'desc' => 'Graduate study, advanced research, and teaching opportunities in the United States.', 'link' => 'https://foreign.fulbrightonline.org', 'source' => 'Fulbright', 'type' => 'Scholarship', 'region' => '🇺🇸 USA', 'date' => ''],
        ['title' => 'DAAD Research Grants', 'desc' => 'Research grants for doctoral candidates and young researchers to conduct research in Germany.', 'link' => 'https://www.daad.de', 'source' => 'DAAD', 'type' => 'Research', 'region' => '🇪🇺 EU', 'date' => ''],
        ['title' => 'Gates Cambridge Scholarship', 'desc' => 'Prestigious international scholarship at the University of Cambridge for outstanding postgraduate students.', 'link' => 'https://www.gatescambridge.org', 'source' => 'Gates Cambridge', 'type' => 'Fellowship', 'region' => '🇬🇧 UK', 'date' => ''],
        ['title' => 'JSPS Postdoctoral Fellowship', 'desc' => 'Opportunities for young foreign researchers to conduct research at Japanese universities.', 'link' => 'https://www.jsps.go.jp', 'source' => 'JSPS', 'type' => 'Research', 'region' => '🇯🇵 Japan', 'date' => ''],
        ['title' => 'Erasmus Mundus Joint Masters', 'desc' => 'Highly integrated international study programmes with monthly stipend across European universities.', 'link' => 'https://eacea.ec.europa.eu/erasmus', 'source' => 'EU Commission', 'type' => 'Scholarship', 'region' => '🇪🇺 EU', 'date' => ''],
    ];

    foreach ($sources as $source) {
        try {
            $response = Http::timeout(10)->get($source['url']);
            if (!$response->successful()) {
                continue;
            }

            $xml = @simplexml_load_string($response->body(), 'SimpleXMLElement', LIBXML_NOCDATA);
            if (! $xml || ! isset($xml->channel->item)) {
                continue;
            }

            foreach ($xml->channel->item as $entry) {
                $title = trim((string) $entry->title);
                $description = trim((string) $entry->description);
                $description = strip_tags($description);
                if (strlen($description) > 160) {
                    $description = substr($description, 0, 157) . '...';
                }

                $items[] = [
                    'title'  => $title,
                    'desc'   => $description,
                    'link'   => trim((string) $entry->link),
                    'date'   => isset($entry->pubDate) ? substr(trim((string) $entry->pubDate), 0, 10) : '',
                    'source' => $source['label'],
                    'type'   => $guessType($title, $source['type']),
                    'region' => $guessRegion($title, $description),
                ];
            }
        } catch (\Exception $e) {
            continue;
        }
    }

    if (count($items) === 0) {
        return response()->json(['status' => 'fallback', 'items' => $fallback]);
    }

    return response()->json(['status' => 'ok', 'items' => $items]);
});

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