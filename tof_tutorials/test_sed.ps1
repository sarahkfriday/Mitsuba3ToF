# Define the file and replacement parameters
$filePath = "test.txt"
$pattern = '<emitter type=".*?">'  # Text to be replaced
$replacement = '"python-default": "llvm_ad_rgb",'  # Replacement text

# Read the file, replace text, and write back
(Get-Content $filePath) -replace $pattern, $replacement | Set-Content $filePath