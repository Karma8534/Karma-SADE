// Quick test script - paste this in Claude.ai console to check DOM structure
console.log("=== Testing DOM Selectors ===");

// Test 1: Find all potential message containers
console.log("\n1. All message-related elements:");
const allMessages = document.querySelectorAll('[class*="message"], [class*="Message"], [data-testid*="message"]');
console.log(`Found ${allMessages.length} elements with 'message' in class/testid`);

// Test 2: Check for font classes (what the extension looks for)
console.log("\n2. Font-based selectors (current extension approach):");
const fontUser = document.querySelectorAll('.font-user-message');
const fontClaude = document.querySelectorAll('.font-claude-message');
console.log(`font-user-message: ${fontUser.length}`);
console.log(`font-claude-message: ${fontClaude.length}`);

// Test 3: Check for data-testid attributes
console.log("\n3. Data-testid approach:");
const userTestId = document.querySelectorAll('[data-testid*="user"]');
const assistantTestId = document.querySelectorAll('[data-testid*="assistant"]');
console.log(`data-testid containing 'user': ${userTestId.length}`);
console.log(`data-testid containing 'assistant': ${assistantTestId.length}`);

// Test 4: Show actual message text if found
console.log("\n4. Sample message content:");
if (allMessages.length > 0) {
    const lastFew = Array.from(allMessages).slice(-4);
    lastFew.forEach((el, i) => {
        const text = el.innerText.trim().substring(0, 100);
        console.log(`Message ${i}: "${text}..."`);
        console.log(`  Classes: ${el.className}`);
        console.log(`  TestID: ${el.getAttribute('data-testid')}`);
    });
}

// Test 5: Look for conversation container
console.log("\n5. Conversation containers:");
const containers = document.querySelectorAll('[data-testid="conversation"], main, [role="main"]');
console.log(`Found ${containers.length} potential conversation containers`);

console.log("\n=== Test Complete ===");
console.log("If font-user-message and font-claude-message are both 0, the selectors need updating.");
