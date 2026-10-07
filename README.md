# Simple Chat App

A small chat app I built to learn React, TypeScript and a bit of backend using Python. Two people log in, see whether the other one is online, and send messages to each other through a tiny Python web server.

It is deliberately simple: no database, no passwords, no fancy libraries, just raw basic concepts and pure code!!

## What's in here

```
.
├── chat-app/        the website (React + TypeScript, built with Vite)
    └── Server.py    the backend (plain Python, nothing to install)
```

## What it does

- A login screen where you enter a display name and an IP address
- A chat screen with a header showing who you're talking to and whether they're online
- Message bubbles: yours on the right in blue, theirs on the left in white
- A message box that clears itself after sending, and a Send button that stays disabled until you type something
- A scrolling message area, so the header and the message box stay put while messages scroll
- A server that holds messages for someone who is offline and hands them over when they come back

## Running it

You'll need [Node.js](https://nodejs.org) (version 20 or newer) and Python 3.

**1. Start the server**

```bash
cd src
python Server.py
```

It runs on http://localhost:8000. Leave this terminal open.

**2. Start the website** (in a second terminal)

```bash
cd chat-app
npm install
npm run dev
```

Open http://localhost:3000.

## How the pieces fit together

The two chat windows never talk to each other directly. They both talk to the server, and the server passes messages along, a bit like a post office.

```
 Person A's browser ──send──▶  ┌───────────┐  ◀──polls every second── Person B's browser
                               │ Server.py │
 Person A's browser ◀─polls──  │  (queue)  │  ──delivers──▶           Person B's browser
                               └───────────┘
```

**Polling:** each browser asks the server "anything new for me?" every second or so. That question also tells the server "I'm still here". If someone hasn't asked for 5 seconds, the server treats them as offline.

**The queue:** when you send a message, the server puts it in the other person's queue, whether they're online or not. Their next poll picks it up. So if your friend shows up an hour later, they still get everything you sent.

**Identifying people:** each person is identified by the IP address they type in. I used typed addresses instead of real ones so both people can test on the same computer (otherwise both would look like `127.0.0.1`).

### The server's three endpoints

| Endpoint | Used for |
|---|---|
| `POST /connect` | Say "I'm here" and who you want to chat with |
| `POST /send` | Put a message in the other person's queue |
| `GET /poll?me=...&peer=...` | Collect new messages and check if the other person is online |

### Trying the server without the website

You can test the server on its own with `curl`:

```bash
# Rishi joins, wanting to chat with 10.0.0.2
curl -X POST localhost:8000/connect -H "Content-Type: application/json" \
  -d '{"me":"10.0.0.1","name":"Rishi","peer":"10.0.0.2"}'

# Rishi sends a message (the other person isn't here yet)
curl -X POST localhost:8000/send -H "Content-Type: application/json" \
  -d '{"from":"10.0.0.1","to":"10.0.0.2","text":"Hi Alex!"}'

# Alex joins later, then asks for his messages
curl -X POST localhost:8000/connect -H "Content-Type: application/json" \
  -d '{"me":"10.0.0.2","name":"Alex","peer":"10.0.0.1"}'
curl "localhost:8000/poll?me=10.0.0.2&peer=10.0.0.1"
```

The last call returns Rishi's waiting message.

## The website's components

Each part of the screen is its own small component:

```
App                   decides: show Login, or show the chat?
├── Login             name + IP address form
└── ChatScreen        the whole chat page, owns the list of messages
    ├── ChatHeader    avatar, name, online / offline
    ├── ChatArena     the scrolling area
    │   └── MessageBubble   one message, left or right
    └── MessageInput  the box and the Send button
```

Every component has its own `.tsx` file and its own `.css` file, in `chat-app/src/components/`. Shared types (like what a `Message` looks like) are in `chat-app/src/types.ts`.

## Where things stand

**Done**
- The full chat screen, with styling
- Login with name and IP address
- The server: connect, send, poll, online status, and the offline message queue (tested with curl, including a user joining late)

**Not done yet**
- **Connecting the website to the server.** Right now the chat screen only shows messages you send locally, and nothing is sent to `Server.py` yet. The next step is calling `/connect` once after login, polling `/poll` every second with `useEffect`, and calling `/send` when you press Send.
- **A second IP field on the login screen.** The server needs to know both your address and your friend's address. At the moment there's only one field.
- Scrolling to the newest message automatically

## Things to know

- Everything lives in the server's memory. If you stop the server, users and waiting messages are gone.
- There's no security at all. Anyone who knows an address could send messages as that person. That's fine for learning, but it isn't something to put on the internet.
- To use it across two computers, run `Server.py` on one of them, and point the website on both at that computer's address instead of `localhost`. You may need to allow Python through the firewall.

## Built with

- [React](https://react.dev) and TypeScript
- [Vite](https://vite.dev) for the dev server and build
- Python's built-in `http.server` for the backend