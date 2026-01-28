# 🥪 SandwishPicnic Frontend

A React-based search interface for the SandwishPicnic Log4j CTF Challenge.

## 🚀 Quick Start

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation & Running

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   - The frontend will run on `http://localhost:5173` (Vite default)
   - Make sure the backend is running on `http://localhost:8080`

## 🔧 Backend Connection

The frontend is configured to connect to the Spring Boot backend at `http://localhost:8080/search`.

### Starting the Complete Application:

**Terminal 1 - Backend:**
```bash
cd ../server
mvn spring-boot:run
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

## 🎯 Features

- **Search Interface:** Clean, responsive search bar
- **Real-time Results:** Displays responses from the backend
- **Error Handling:** Shows connection errors and validation messages
- **Mobile Responsive:** Works on desktop and mobile devices

## 🎮 For CTF Participants

This frontend provides an easy way to interact with the vulnerable Log4j endpoints:

- **Search Endpoint:** `GET /search?query=<your-input>`
- **Login Endpoint:** Available at `http://localhost:8080/login?username=<input>` (direct access)

### Example Usage:
1. Enter a search term in the search box
2. Click "Search" to send the query to the backend
3. View the server response below

### For Log4j Exploitation:
- Use the search interface to test JNDI injection payloads
- The input is sent directly to the vulnerable logging endpoint
- Monitor your LDAP server for incoming requests

## 🛠️ Development

### Available Scripts:
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

### Tech Stack:
- React 18
- Vite
- Modern CSS with responsive design

## 🔗 Related Files:
- Backend: `../server/` (Spring Boot application)
- CTF Guide: `../server/CTF-CHALLENGE-GUIDE.md`
- Exploitation Guide: `../server/CTF-EXPLOITATION-GUIDE.md`
