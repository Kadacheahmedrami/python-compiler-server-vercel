async function testAPI() {
    const baseUrl = 'https://python-compiler-server-vercel.vercel.app';
    
    console.log('🔍 Testing Fixed API...');
    console.log(`🌐 URL: ${baseUrl}`);
    
    // Test data
    const testData = {
        expr: 'expr("P & Q")'
    };
    
    try {
        console.log('1️⃣ Testing POST request with proper data...');
        const response = await fetch(baseUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(testData)
        });
        
        console.log(`Status: ${response.status}`);
        console.log(`Status Text: ${response.statusText}`);
        
        const responseText = await response.text();
        console.log('📄 Raw Response:');
        console.log(responseText);
        
        // Try to parse as JSON
        try {
            const jsonResponse = JSON.parse(responseText);
            console.log('✅ Parsed JSON Response:');
            console.log(JSON.stringify(jsonResponse, null, 2));
        } catch (parseError) {
            console.log('❌ Failed to parse as JSON:', parseError.message);
        }
        
    } catch (error) {
        console.error('❌ Request failed:', error.message);
    }
    
    console.log('\n2️⃣ Testing different expressions...');
    const testExpressions = [
        'expr("A")',
        'expr("P | Q")',
        'expr("(P & Q) => R")'
    ];
    
    for (const expr of testExpressions) {
        try {
            console.log(`\n🎯 Testing expression: ${expr}`);
            const response = await fetch(baseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ expr })
            });
            
            const result = await response.json();
            console.log(`   Status: ${response.status}`);
            console.log(`   Result: ${JSON.stringify(result)}`);
            
        } catch (error) {
            console.log(`   Error: ${error.message}`);
        }
    }
}

testAPI();