/**
 * Material Symbols Configuration
 * This file configures and initializes Material Symbols icons for the application
 */

// Function to check if Material Symbols font is loaded
function checkMaterialSymbolsLoaded() {
  // Log for debugging
  console.log('Checking Material Symbols font loading...');
  
  // Create a span with a material symbol to test
  const testEl = document.createElement('span');
  testEl.className = 'material-symbols-outlined';
  testEl.textContent = 'check';
  testEl.style.position = 'absolute';
  testEl.style.opacity = '0';
  
  // Add to DOM temporarily to check rendering
  document.body.appendChild(testEl);
  
  // Get computed style and check if font is loaded
  const computedStyle = window.getComputedStyle(testEl);
  const fontFamily = computedStyle.getPropertyValue('font-family');
  
  // Clean up
  document.body.removeChild(testEl);
  
  // Log font status
  const isFontLoaded = fontFamily.includes('Material Symbols Outlined');
  console.log(`Material Symbols font loaded: ${isFontLoaded}`);
  
  // If not loaded, try to reload or notify
  if (!isFontLoaded) {
    console.warn('Material Symbols font not loaded correctly. Attempting to reload...');
    // Attempt to reload the font by adding the link dynamically
    ensureFontIsLoaded();
  }
}

// Function to ensure the font is loaded
function ensureFontIsLoaded() {
  // Check if we already have the Material Symbols font link
  const existingLink = document.querySelector('link[href*="Material+Symbols+Outlined"]');
  
  if (!existingLink) {
    console.log('Adding Material Symbols font link dynamically');
    const fontLink = document.createElement('link');
    fontLink.rel = 'stylesheet';
    fontLink.href = 'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,0..200';
    document.head.appendChild(fontLink);
  }
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    setTimeout(checkMaterialSymbolsLoaded, 1000); // Delay check to ensure font has time to load
  });
} else {
  // DOM already loaded, check after a short delay
  setTimeout(checkMaterialSymbolsLoaded, 1000);
}

// Export for explicit import if needed
export default {
  checkMaterialSymbolsLoaded,
  ensureFontIsLoaded
}; 