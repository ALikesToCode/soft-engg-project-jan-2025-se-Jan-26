# Lecture Transcription and AI Summary Features

## Overview

This documentation describes the lecture transcription and AI summary features added to the course platform. These features enhance the learning experience by providing:

1. **Lecture Transcriptions**: Automatically extracted text from video lectures, making content more accessible and searchable.
2. **AI-Generated Summaries**: Concise summaries of lecture content to help students quickly understand key points.
3. **AI Chat Context**: Improved AI assistant that can reference lecture transcripts and summaries when answering questions.

## Feature Components

### Backend Components

1. **Database Models**:
   - `LectureTranscription`: Stores the full text transcription and AI-generated summary for each lecture.

2. **API Endpoints**:
   - `GET /api/v1/transcription/{lecture_id}`: Retrieve transcription for a specific lecture
   - `POST /api/v1/transcription/`: Create a new transcription
   - `PUT /api/v1/transcription/{lecture_id}`: Update an existing transcription
   - `DELETE /api/v1/transcription/{lecture_id}`: Delete a transcription
   - `POST /api/v1/transcription/extract/{lecture_id}`: Extract transcription from a video URL
   - `POST /api/v1/transcription/summary`: Generate an AI summary for a lecture transcription

3. **Services**:
   - `TranscriptService`: Handles CRUD operations for transcriptions and generates AI summaries
   - `YouTubeTranscriptService`: Extracts transcripts from YouTube videos

4. **Enhanced AI Chat**:
   - The chat service now incorporates lecture transcriptions and summaries in the context when responding to questions about specific lectures.

### Frontend Components

1. **Transcription Component**:
   - Located in the course lecture view with its own tab
   - Features transcript viewing with search functionality
   - Displays AI-generated summary
   - Allows generation of transcript if not available
   - Provides copy-to-clipboard functionality

2. **Chat Integration**:
   - Chat assistant is aware of lecture context
   - Can reference transcription content in responses
   - Seamlessly integrates with the learning experience

## User Workflows

### Viewing a Transcript

1. Navigate to a course lecture
2. Click on the "Transcript & Summary" tab
3. View the transcript with paragraph formatting for readability
4. Use the search function to find specific topics within the transcript

### Generating a Missing Transcript

1. If a lecture has no transcript, a "Generate Transcript" button will appear
2. Click this button to extract the transcript from the video source
3. The system will automatically process the video (currently supporting YouTube videos)
4. Once complete, the transcript will be displayed

### Viewing the AI Summary

1. In the "Transcript & Summary" tab, click on the "AI Summary" tab
2. View the concise AI-generated summary of key lecture points
3. If no summary exists, click "Generate Summary" to create one

### Using AI Chat with Transcript Context

1. When viewing a lecture, the AI chat is automatically aware of the lecture context
2. Ask questions about the lecture content
3. The AI will reference both the lecture content and the transcript in its responses
4. For more specific answers, the AI can leverage detailed information from the transcript

## Technical Implementation Notes

### Transcript Extraction

- Currently supports YouTube videos through their transcript API
- The system makes API calls to retrieve available transcripts
- If multiple languages are available, it prioritizes English

### AI Summary Generation

- Uses the LLM framework to generate concise, accurate summaries
- Summaries aim to capture key points, concepts, and explanations
- For very long transcripts, the system processes chunks to stay within token limits

### Database Structure

- The `LectureTranscription` model relates to the `Lecture` model via a foreign key
- Each lecture can have only one transcription record
- Both the full transcript and the AI summary are stored as text fields

## Future Enhancements

- Support for more video platforms beyond YouTube
- Real-time transcript generation for uploaded videos
- Improved AI summarization with section highlighting
- Interactive transcript that synchronizes with video playback
- Transcript annotations and note-taking features

## Troubleshooting

If you encounter issues with transcript generation:
1. Ensure the video URL is accessible and contains captions/subtitles
2. For YouTube videos, check that the creator has enabled subtitles
3. If automatic extraction fails, manual transcription can be added via the API 