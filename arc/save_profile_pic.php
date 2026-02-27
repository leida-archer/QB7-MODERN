<?php
header('Content-Type: application/json');

$raw = file_get_contents('php://input');
$data = json_decode($raw, true);

if (!$data || empty($data['username']) || empty($data['type']) || empty($data['data'])) {
    echo json_encode(['error' => 'Missing fields']);
    exit;
}

$username = preg_replace('/[^a-z0-9_]/', '', strtolower($data['username']));
$type = ($data['type'] === 'cover') ? 'cover' : 'profile';
$filename = $type . '_' . $username . '.jpg';
$path = 'FacePics/' . $filename;

// Decode base64 data URL
$base64 = preg_replace('/^data:image\/\w+;base64,/', '', $data['data']);
$imageData = base64_decode($base64);

if (!$imageData) {
    echo json_encode(['error' => 'Invalid image data']);
    exit;
}

file_put_contents($path, $imageData);

// Update manifest
$manifest_path = 'FacePics/profiles.json';
$manifest = [];
if (file_exists($manifest_path)) {
    $manifest = json_decode(file_get_contents($manifest_path), true) ?: [];
}
if (!isset($manifest[$username])) {
    $manifest[$username] = [];
}
$manifest[$username][$type] = $filename . '?v=' . time();

file_put_contents($manifest_path, json_encode($manifest));

echo json_encode(['success' => true, 'path' => $path]);
?>
