async function testEnhancedLogicAPI() {
    const baseUrl = 'https://python-compiler-server-vercel.vercel.app';
    
    console.log('🔍 Testing Enhanced Python Logic API...');
    console.log(`🌐 URL: ${baseUrl}`);
    
    // Helper function to test expressions
    async function testExpression(expr, description = '') {
        try {
            console.log(`\n🎯 ${description || 'Testing'}: ${expr.replace(/\n/g, '; ')}`);
            
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
                if (result.cleaned_expression) {
                    console.log(`   🧹 Cleaned: ${result.cleaned_expression}`);
                }
                console.log(`   📚 AIMA Available: ${result.aima_available}`);
            } else {
                console.log(`   ❌ Error: ${result.error}`);
                if (result.details && result.details.length < 200) {
                    console.log(`   📝 Details: ${result.details}`);
                }
            }
            
            return { success: response.ok, result };
            
        } catch (error) {
            console.log(`   ❌ Request failed: ${error.message}`);
            return { success: false, error: error.message };
        }
    }
    
    console.log('\n1️⃣ Testing basic expressions...');
    const basicTests = [
        { expr: 'expr("P & Q")', desc: 'Conjunction' },
        { expr: 'expr("P | Q")', desc: 'Disjunction' },
        { expr: 'expr("P >> Q")', desc: 'Implication' },
        { expr: 'expr("~P")', desc: 'Negation' },
        { expr: 'PropKB()', desc: 'Empty KB' },
    ];
    
    for (const test of basicTests) {
        await testExpression(test.expr, test.desc);
    }
    
    console.log('\n2️⃣ Testing truth evaluation...');
    const truthTests = [
        { 
            expr: 'pl_true(expr("P"), {"P": True})', 
            desc: 'Simple truth check - P is True' 
        },
        { 
            expr: 'pl_true(expr("P"), {"P": False})', 
            desc: 'Simple truth check - P is False' 
        },
        { 
            expr: 'pl_true(expr("P & Q"), {"P": True, "Q": True})', 
            desc: 'Conjunction truth - both True' 
        },
        { 
            expr: 'pl_true(expr("P & Q"), {"P": True, "Q": False})', 
            desc: 'Conjunction truth - one False' 
        },
        { 
            expr: 'pl_true(expr("P | Q"), {"P": False, "Q": True})', 
            desc: 'Disjunction truth - one True' 
        },
    ];
    
    for (const test of truthTests) {
        await testExpression(test.expr, test.desc);
    }
    
    console.log('\n3️⃣ Testing knowledge base operations...');
    const kbTests = [
        { 
            expr: `kb = PropKB()
kb.tell(expr("P"))
str(kb)`, 
            desc: 'KB with one fact' 
        },
        { 
            expr: `kb = PropKB()
kb.tell(expr("P"))
kb.ask(expr("P"))`, 
            desc: 'Query known fact' 
        },
        { 
            expr: `kb = PropKB()
kb.tell(expr("P"))
kb.ask(expr("Q"))`, 
            desc: 'Query unknown fact' 
        },
        { 
            expr: `kb = PropKB()
kb.tell(expr("P >> Q"))
kb.tell(expr("P"))
kb.ask(expr("Q"))`, 
            desc: 'Simple modus ponens inference' 
        },
    ];
    
    for (const test of kbTests) {
        await testExpression(test.expr, test.desc);
    }
    
    console.log('\n4️⃣ Testing logical operations...');
    const logicalTests = [
        { 
            expr: `p = expr("P")
q = expr("Q")
p & q`, 
            desc: 'Expression conjunction' 
        },
        { 
            expr: `p = expr("P")
q = expr("Q")
p | q`, 
            desc: 'Expression disjunction' 
        },
        { 
            expr: `p = expr("P")
~p`, 
            desc: 'Expression negation' 
        },
    ];
    
    for (const test of logicalTests) {
        await testExpression(test.expr, test.desc);
    }
    
    console.log('\n5️⃣ Testing satisfiability...');
    const satTests = [
        { 
            expr: 'dpll_satisfiable(expr("P & Q"))', 
            desc: 'Satisfiable formula' 
        },
        { 
            expr: 'dpll_satisfiable(expr("P & ~P"))', 
            desc: 'Unsatisfiable formula' 
        },
        { 
            expr: 'dpll_satisfiable(expr("P | Q"))', 
            desc: 'Disjunction satisfiability' 
        },
    ];
    
    for (const test of satTests) {
        await testExpression(test.expr, test.desc);
    }
    
    console.log('\n6️⃣ Testing expressions with imports (should be cleaned)...');
    const importTests = [
        { 
            expr: `from aima3.logic import *
expr("P & Q")`, 
            desc: 'Expression with import' 
        },
        { 
            expr: `from aima3.logic import dpll_satisfiable
dpll_satisfiable(expr("P & Q"))`, 
            desc: 'Function call with import' 
        },
    ];
    
    for (const test of importTests) {
        await testExpression(test.expr, test.desc);
    }
    
    console.log('\n📊 Test Summary Complete!');
    console.log('🔧 The API should now handle:');
    console.log('   ✅ Basic logical expressions');
    console.log('   ✅ Truth evaluations');
    console.log('   ✅ Knowledge base operations');
    console.log('   ✅ Import statement filtering');
    console.log('   ✅ Enhanced mock implementations');
}

// Run the tests
testEnhancedLogicAPI().catch(console.error);