from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)

# Each API has its own independent message list
messages = {
    "hello1": ["Hello, World! from API 1"],
    "hello2": ["Hello, World! from API 2"],
    "hello3": ["Hello, World! from API 3"]
}

API_NAMES = {
    "hello1": "API 1",
    "hello2": "API 2",
    "hello3": "API 3"
}


# Dashboard web page
@app.route("/")
def dashboard():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Hello World API Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1000px;
                margin: 40px auto;
                padding: 0 20px;
                background: #f4f6f9;
                color: #222;
            }
            h1 { color: #17365d; }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
            }
            .card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 8px #0001;
            }
            input {
                box-sizing: border-box;
                width: 100%;
                padding: 10px;
                margin: 8px 0;
            }
            button {
                padding: 10px 14px;
                background: #17365d;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
            li { margin: 10px 0; overflow-wrap: anywhere; }
            .endpoint { color: #555; font-size: 13px; }
            #status { margin: 15px 0; }
        </style>
    </head>
    <body>
        <h1>Hello World API Dashboard</h1>
        <p>Three APIs. Three message lists. One dashboard.</p>
        <p id="status">Loading messages...</p>

        <div class="grid">
            <div class="card">
                <h2>API 1</h2>
                <p class="endpoint">GET /api/hello1</p>
                <ul id="hello1"></ul>
                <form onsubmit="addMessage(event, 'hello1')">
                    <input id="input-hello1"
                           placeholder="Enter a message" required>
                    <button type="submit">Add Message</button>
                </form>
            </div>

            <div class="card">
                <h2>API 2</h2>
                <p class="endpoint">GET /api/hello2</p>
                <ul id="hello2"></ul>
                <form onsubmit="addMessage(event, 'hello2')">
                    <input id="input-hello2"
                           placeholder="Enter a message" required>
                    <button type="submit">Add Message</button>
                </form>
            </div>

            <div class="card">
                <h2>API 3</h2>
                <p class="endpoint">GET /api/hello3</p>
                <ul id="hello3"></ul>
                <form onsubmit="addMessage(event, 'hello3')">
                    <input id="input-hello3"
                           placeholder="Enter a message" required>
                    <button type="submit">Add Message</button>
                </form>
            </div>
        </div>

        <script>
            async function loadMessages() {
                try {
                    for (const api of ["hello1", "hello2", "hello3"]) {
                        const response = await fetch("/api/" + api);
                        if (!response.ok) throw new Error("API request failed");

                        const data = await response.json();
                        const list = document.getElementById(api);
                        list.replaceChildren();

                        data.messages.forEach(message => {
                            const item = document.createElement("li");
                            item.textContent = message;
                            list.appendChild(item);
                        });
                    }
                    document.getElementById("status").textContent =
                        "All APIs connected successfully.";
                } catch (error) {
                    document.getElementById("status").textContent =
                        "Error loading messages: " + error.message;
                }
            }

            async function addMessage(event, api) {
                event.preventDefault();

                const input = document.getElementById("input-" + api);
                const message = input.value.trim();
                if (!message) return;

                try {
                    const response = await fetch("/api/" + api, {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({message: message})
                    });

                    const data = await response.json();
                    if (!response.ok) throw new Error(data.error);

                    input.value = "";
                    await loadMessages();
                } catch (error) {
                    document.getElementById("status").textContent =
                        "Error adding message: " + error.message;
                }
            }

            loadMessages();
        </script>
    </body>
    </html>
    """)


# Shared handler for all three APIs
def handle_api(api):
    if request.method == "GET":
        return jsonify({
            "api": API_NAMES[api],
            "messages": messages[api]
        })

    data = request.get_json(silent=True) or {}
    message = data.get("message")

    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "A non-empty message is required"}), 400

    if len(message) > 500:
        return jsonify({"error": "Message must be 500 characters or fewer"}), 400

    messages[api].append(message.strip())

    return jsonify({
        "api": API_NAMES[api],
        "message": message.strip(),
        "total_messages": len(messages[api])
    }), 201


@app.route("/api/hello1", methods=["GET", "POST"])
def hello1():
    return handle_api("hello1")


@app.route("/api/hello2", methods=["GET", "POST"])
def hello2():
    return handle_api("hello2")


@app.route("/api/hello3", methods=["GET", "POST"])
def hello3():
    return handle_api("hello3")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
