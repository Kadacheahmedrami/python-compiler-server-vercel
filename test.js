// Test script for Python Code Runner API
// Usage: node test.js

const BASE_URL = 'http://localhost:5000'; // Change this to your deployed URL

async function testAPI() {
    console.log('🚀 Testing Python Code Runner API\n');

    // Test 1: Welcome route
    console.log('📍 Test 1: Welcome Route');
    try {
        const response = await fetch(`${BASE_URL}/`);
        const text = await response.text();
        console.log(`✅ GET / - Status: ${response.status}`);
        console.log(`📄 Response: ${text}\n`);
    } catch (error) {
        console.log(`❌ GET / - Error: ${error.message}\n`);
    }

    // Test 2: Simple print statement
    console.log('📍 Test 2: Simple Print Statement');
    await testCode({
        code: "print('Hello from Python!')"
    }, 'Simple print');

    // Test 3: Mathematical operations
    console.log('📍 Test 3: Mathematical Operations');
    await testCode({
        code: `
result = 10 + 5
print(f"10 + 5 = {result}")
power = 2 ** 8
print(f"2^8 = {power}")
        `.trim()
    }, 'Math operations');

    // Test 4: Variables and loops
    console.log('📍 Test 4: Variables and Loops');
    await testCode({
        code: `
numbers = [1, 2, 3, 4, 5]
total = 0
for num in numbers:
    total += num
print(f"Sum of {numbers} = {total}")

# List comprehension
squares = [x**2 for x in range(1, 6)]
print(f"Squares: {squares}")
        `.trim()
    }, 'Variables and loops');

    // Test 5: Error handling - Syntax error
    console.log('📍 Test 5: Syntax Error');
    await testCode({
        code: "print('Hello world'"  // Missing closing parenthesis
    }, 'Syntax error');

    // Test 6: Error handling - Runtime error
    console.log('📍 Test 6: Runtime Error');
    await testCode({
        code: `
x = 10
y = 0
result = x / y  # Division by zero
print(result)
        `.trim()
    }, 'Runtime error');

    // Test 7: Import modules
    console.log('📍 Test 7: Import Modules');
    await testCode({
        code: `
import math
import random

print(f"Pi: {math.pi}")
print(f"Square root of 16: {math.sqrt(16)}")
print(f"Random number: {random.randint(1, 100)}")
        `.trim()
    }, 'Import modules');

    // Test 8: JSON and data structures
    console.log('📍 Test 8: JSON and Data Structures');
    await testCode({
        code: `
import json

data = {
    "name": "Python Runner",
    "version": "1.0",
    "features": ["code execution", "error handling", "output capture"]
}

json_str = json.dumps(data, indent=2)
print("JSON Data:")
print(json_str)

# Parse back
parsed = json.loads(json_str)
print(f"\\nName: {parsed['name']}")
        `.trim()
    }, 'JSON handling');

    // Test 9: No code provided
    console.log('📍 Test 9: No Code Provided');
    await testCode({}, 'No code');

    // Test 10: Empty code
    console.log('📍 Test 10: Empty Code');
    await testCode({
        code: ""
    }, 'Empty code');

    console.log('🏁 All tests completed!');
}

async function testCode(payload, testName) {
    try {
        const response = await fetch(`${BASE_URL}/code`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        
        console.log(`Status: ${response.status}`);
        
        if (result.success) {
            console.log('✅ Success');
            if (result.stdout) {
                console.log('📤 Output:');
                console.log(result.stdout);
            }
            if (result.stderr) {
                console.log('⚠️  Stderr:');
                console.log(result.stderr);
            }
        } else {
            console.log('❌ Error');
            console.log(`Error: ${result.error}`);
            if (result.traceback) {
                console.log('📋 Traceback:');
                console.log(result.traceback);
            }
        }
        
    } catch (error) {
        console.log(`❌ Network Error: ${error.message}`);
    }
    
    console.log('─'.repeat(50) + '\n');
}

// Helper function to test with custom URL
function setBaseURL(url) {
    BASE_URL = url;
}

// Run tests if this file is executed directly
if (require.main === module) {
    // Check if custom URL is provided as command line argument
    const customURL = process.argv[2];
    if (customURL) {
        console.log(`🔗 Using custom URL: ${customURL}`);
        BASE_URL = customURL;
    } else {
        console.log(`🔗 Using default URL: ${BASE_URL}`);
        console.log('💡 Tip: You can provide a custom URL as argument: node test.js https://your-app.vercel.app');
    }
    
    testAPI().catch(console.error);
}

// Export for use in other files
module.exports = { testAPI, setBaseURL };