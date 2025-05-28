async function testLogicAPI() {
    const baseUrl = 'https://python-compiler-server-vercel.vercel.app';
    
    console.log('🔍 Testing Python Logic API...');
    console.log(`🌐 URL: ${baseUrl}`);
    
    // Test expressions for AIMA3 logic
    const testExpressions = [
        'expr("P & Q")',
        'expr("P | Q")',
        'expr("(P & Q) => R")',
        'kb = PropKB(); kb.tell(expr("P")); kb',
        'kb = PropKB(); kb.tell(expr("P & Q")); kb.ask(expr("P"))',
        'pl_true({"P": True, "Q": False}, expr("P | Q"))'
    ];
    
    console.log('\n1️⃣ Testing GET request (API info)...');
    try {
        const response = await fetch(baseUrl);
        const result = await response.json();
        console.log('✅ API Info:', JSON.stringify(result, null, 2));
    } catch (error) {
        console.log('❌ GET request failed:', error.message);
    }
    
    console.log('\n2️⃣ Testing Python logic handler directly...');
    try {
        const response = await fetch(`${baseUrl}/api/logic`);
        const result = await response.json();
        console.log('✅ Python Handler Info:', JSON.stringify(result, null, 2));
    } catch (error) {
        console.log('❌ Python handler test failed:', error.message);
    }
    
    console.log('\n3️⃣ Testing logic expressions...');
    for (const expr of testExpressions) {
        try {
            console.log(`\n🎯 Testing: ${expr}`);
            
            const response = await fetch(baseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ expr })
            });
            
            const result = await response.json();
            console.log(`   Status: ${response.status}`);
            
            if (response.ok) {
                console.log(`   ✅ Result: ${JSON.stringify(result.result)}`);
                if (result.aima_available !== undefined) {
                    console.log(`   📚 AIMA3 Available: ${result.aima_available}`);
                }
            } else {
                console.log(`   ❌ Error: ${JSON.stringify(result, null, 2)}`);
            }
            
        } catch (error) {
            console.log(`   ❌ Request failed: ${error.message}`);
        }
    }
    
    console.log('\n4️⃣ Testing multi-line expressions...');
    const multiLineExpr = `kb = PropKB()
kb.tell(expr("P"))
kb.tell(expr("Q"))
kb.ask(expr("P & Q"))`;
    
    try {
        console.log('🎯 Testing multi-line expression...');
        const response = await fetch(baseUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ expr: multiLineExpr })
        });
        
        const result = await response.json();
        console.log(`   Status: ${response.status}`);
        
        if (response.ok) {
            console.log(`   ✅ Result: ${JSON.stringify(result.result)}`);
        } else {
            console.log(`   ❌ Error: ${JSON.stringify(result, null, 2)}`);
        }
        
    } catch (error) {
        console.log(`   ❌ Multi-line test failed: ${error.message}`);
    }
}

testLogicAPI();