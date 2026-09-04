<?php
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('Referrer-Policy: no-referrer');
header('Permissions-Policy: camera=(), microphone=(), geolocation=()');

if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    http_response_code(405);
    header('Allow: GET');
    echo json_encode(['error'=>'method_not_allowed']);
    exit;
}
$action = $_GET['action'] ?? 'health';
if (!is_string($action) || !preg_match('/^[a-z_]{1,32}$/', $action)) {
    http_response_code(400); echo json_encode(['error'=>'invalid_action']); exit;
}
if ($action === 'health') {
    echo json_encode(['status'=>'ok','service'=>'pulsenet-php','free'=>true,'time'=>time()]); exit;
}
if ($action === 'version') {
    echo json_encode(['service'=>'pulsenet-php','api_version'=>'v3','free'=>true]); exit;
}
http_response_code(404);
echo json_encode(['error'=>'not_found']);
