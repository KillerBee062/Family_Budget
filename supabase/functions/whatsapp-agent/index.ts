import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"
import { GoogleGenerativeAI } from "https://esm.sh/@google/generative-ai@0.1.0"

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!
const SUPABASE_ANON_KEY = Deno.env.get("SUPABASE_ANON_KEY")!
const GEMINI_API_KEY = Deno.env.get("GEMINI_API_KEY")!

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
const genAI = new GoogleGenerativeAI(GEMINI_API_KEY)

serve(async (req) => {
    try {
        // 1. Parse Twilio Request (Form Data)
        const formData = await req.formData()
        const incomingMsg = formData.get("Body") as string
        const from = formData.get("From") as string // User's WhatsApp number

        if (!incomingMsg) return new Response("No message", { status: 400 })

        // 2. Fetch Categories for Context
        const { data: categories } = await supabase
            .from("category_budgets")
            .select("category, group_name")

        const categoriesStr = categories?.map(c => `${c.category} (${c.group_name})`).join(", ") || "Others"

        // 3. Prepare Gemini Agent
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" })

        const prompt = `
      You are a Budget Assistant. Extract financial data from: "${incomingMsg}"
      Categories: ${categoriesStr}
      
      Rules:
      - Log spending as an expense.
      - Log receiving as income.
      - Default paid_by to 'Hadi'.
      
      Call the appropriate function for the transaction.
    `

        // Define tools for Gemini (Using function declarations)
        const tools = [{
            functionDeclarations: [
                {
                    name: "log_expense",
                    description: "Logs an expense transaction",
                    parameters: {
                        type: "object",
                        properties: {
                            item: { type: "string" },
                            amount: { type: "number" },
                            category: { type: "string" },
                            notes: { type: "string" }
                        },
                        required: ["item", "amount", "category"]
                    }
                },
                {
                    name: "log_income",
                    description: "Logs an income transaction",
                    parameters: {
                        type: "object",
                        properties: {
                            source: { type: "string" },
                            amount: { type: "number" },
                            notes: { type: "string" }
                        },
                        required: ["source", "amount"]
                    }
                }
            ]
        }]

        const chat = model.startChat({ tools })
        const result = await chat.sendMessage(prompt)
        const call = result.response.functionCalls()?.[0]

        let responseMsg = "I processed your request, but wasn't sure what to log."

        if (call) {
            if (call.name === "log_expense") {
                const { item, amount, category, notes } = call.args as any
                await supabase.from("expenses").insert({
                    id: crypto.randomUUID(),
                    date: new Date().toISOString().split('T')[0],
                    item, amount, category, notes, paid_by: "Hadi"
                })
                responseMsg = `✅ Logged Expense: ৳${amount} for ${item} (${category})`
            } else if (call.name === "log_income") {
                const { source, amount, notes } = call.args as any
                await supabase.from("income").insert({
                    id: crypto.randomUUID(),
                    date: new Date().toISOString().split('T')[0],
                    source, amount, notes
                })
                responseMsg = `💰 Logged Income: ৳${amount} from ${source}`
            }
        } else {
            responseMsg = result.response.text()
        }

        // 4. Return TwiML (XML) response for WhatsApp
        const twiml = `<?xml version="1.0" encoding="UTF-8"?><Response><Message>${responseMsg}</Message></Response>`

        return new Response(twiml, {
            headers: { "Content-Type": "text/xml" }
        })

    } catch (err) {
        console.error(err)
        return new Response("Internal Error", { status: 500 })
    }
})
