# Rabbit Hole

Rabbit Hole is a personalized web application that tailors content and resources based on user interests. This innovative platform creates a dynamic and engaging experience for users, allowing them to explore topics in-depth and discover new areas of interest.

## Features

1. **User Interests**: Users can index and store their personalized interests, creating a unique profile that informs the content they see.

2. **Personalized Search**: The application generates tailored pages based on user searches, providing relevant and customized information.

3. **Hyperlinked Subtopics**: Within the generated content, relevant subtopics and potential follow-up topics are hyperlinked, encouraging further exploration.

4. **STEM Queries Handling**: For STEM-based queries, Rabbit Hole incorporates a LaTeX interpreter and integrates with an LLM to generate animations using Manim, enhancing the learning experience for technical topics.

5. **Chat Assistant**: A chat assistant is available for user queries, with the added functionality of highlighting specific portions of text for more focused questions.

6. **Dynamic Content Generation**: Each hyperlink click generates a new personalized page, incorporating all the application's features and adding the new topic to the user's interests.

7. **Music Queries**: For music-related queries, Rabbit Hole integrates with Suno to generate relevant music snippets in the appropriate style.

## Technologies Used

- **Backend**: Flask (Python) for handling API requests
- **Database**: PostgreSQL for user data storage
- **Frontend**: React for the user interface
- **API Communication**: Axios for making API calls
- **LLM Integration**: Modal for LLM inference
- **Chat Interface**: Baseten for chat interfacing
- **Music Generation**: TuneHQ (if applicable) and Suno for music-related queries

## Setup Instructions

### Backend Setup

1. Navigate to the `backend` directory.
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up PostgreSQL and update the database URI in `app.py`.
4. Run the Flask app:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to the `frontend` directory.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the React app:
   ```bash
   npm start
   ```

## Project Structure

```
rabbit-hole/
├── backend/
│   ├── app.py
│   └── requirements.txt
└── frontend/
    ├── public/
    ├── src/
    │   ├── App.js
    │   └── ...
    ├── package.json
    └── ...
```

## Future Enhancements

- Integration with fetch.ai for agentic applications
- Improved personalization algorithms
- Mobile application development

## Contributing

We welcome contributions to the Rabbit Hole project. Please read our contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License.