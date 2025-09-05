# 💻 Gemini Coding Chatbot

A modern, feature-rich coding assistant powered by Google's Gemini AI, built with Streamlit and PostgreSQL. Get instant help with coding questions, debug issues, generate code snippets, and learn programming concepts in a sleek, ChatGPT-style interface.

![Chatbot Demo](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue)

## ✨ Features

### 🤖 **AI-Powered Coding Assistant**
- **Smart Code Generation** - Generate code snippets in any programming language
- **Bug Debugging** - Get help identifying and fixing code issues
- **Code Explanation** - Understand complex code with detailed explanations
- **Best Practices** - Learn industry-standard coding practices and patterns

### 💬 **Modern Chat Interface**
- **Persistent Conversations** - All chats saved to database automatically
- **Multiple Chat Sessions** - Create and manage multiple coding conversations
- **Real-time Responses** - Fast, streaming responses from Gemini AI
- **Markdown Support** - Properly formatted code blocks with syntax highlighting

### 👤 **User Management**
- **Secure Authentication** - Email/password login with encrypted storage
- **Password Reset** - Built-in password recovery system
- **Session Persistence** - Stay logged in across browser refreshes
- **User Profiles** - Personalized experience with user avatars

### 🗂️ **Chat Management**
- **Auto-Generated Titles** - Smart conversation titles based on content
- **Delete Conversations** - Clean up old chats with one click
- **Active Chat Highlighting** - Clear visual indication of current conversation
- **Responsive Design** - Works perfectly on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   # Gemini AI Configuration
   GOOGLE_API_KEY=your_gemini_api_key_here
   
   # Database Configuration
   DATABASE_URL=postgresql://username:password@localhost:5432/chatbot_db
   # OR use individual variables:
   PGUSER=your_db_user
   PGPASSWORD=your_db_password
   PGHOST=localhost
   PGPORT=5432
   PGDATABASE=chatbot_db
   PGSSLMODE=disable
   ```

4. **Set up the database**
   The application will automatically create the necessary tables on first run.

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Access the app**
   Open your browser and go to `http://localhost:8501`

## 📁 Project Structure

```
chatbot/
├── app.py                 # Main Streamlit application
├── services/             
│   ├── auth_service.py    # User authentication & password reset
│   ├── conversation_service.py  # Chat management & persistence
│   ├── db_service.py      # Database connection & migrations
│   └── title_service.py   # Auto-generate chat titles
├── .env                   # Environment variables (create this)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GOOGLE_API_KEY` | Your Gemini AI API key | Yes | - |
| `DATABASE_URL` | Complete PostgreSQL connection string | No | - |
| `PGUSER` | Database username | No | postgres |
| `PGPASSWORD` | Database password | No | postgres |
| `PGHOST` | Database host | No | localhost |
| `PGPORT` | Database port | No | 5432 |
| `PGDATABASE` | Database name | No | chatbot |
| `PGSSLMODE` | SSL mode for database | No | disable |

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the generated key to your `.env` file

## 💾 Database Schema

The application automatically creates these tables:

- **`app_users`** - User accounts with encrypted passwords
- **`conversations`** - Chat sessions with timestamps and titles
- **`messages`** - Individual messages with role (user/assistant) and content
- **`reset_tokens`** - Password reset tokens with expiration

## 🎨 Features in Detail

### Smart Code Generation
Ask questions like:
- "Create a Python function to sort a list"
- "Write a REST API endpoint in Node.js"
- "Generate a responsive CSS navbar"

### Debugging Assistant
Get help with:
- Error message explanations
- Code review and optimization
- Performance improvement suggestions
- Security best practices

### Learning Companion
Learn through:
- Step-by-step explanations
- Code pattern examples
- Algorithm implementations
- Framework tutorials

## 🔒 Security Features

- **Password Encryption** - Bcrypt hashing for all user passwords
- **JWT Tokens** - Secure session management
- **SQL Injection Protection** - Parameterized queries throughout
- **Input Validation** - Comprehensive validation on all user inputs
- **Session Timeout** - Automatic logout for security

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment
1. Set up a PostgreSQL database
2. Configure environment variables for production
3. Deploy to your preferred platform (Streamlit Cloud, Heroku, etc.)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists

**Gemini API Error**
- Verify API key is correct
- Check API key permissions
- Ensure you have Gemini API access

**Login Issues**
- Clear browser cache and cookies
- Check database connectivity
- Verify user exists in database

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Open an issue on GitHub
3. Review the code documentation in the services folder

## 🔄 Updates & Roadmap

- [x] User authentication and session management
- [x] Persistent chat conversations
- [x] Password reset functionality
- [x] Modern UI with delete functionality
- [ ] Export chat conversations
- [ ] Theme customization (light/dark mode)
- [ ] File upload and analysis
- [ ] Code execution environment

---

**Built with ❤️ using Streamlit, Gemini AI, and PostgreSQL**