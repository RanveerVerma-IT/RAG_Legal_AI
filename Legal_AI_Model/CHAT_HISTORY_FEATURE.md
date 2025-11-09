# Chat History Feature

## Overview

The system now includes a ChatGPT-like chat history feature that allows users to:
- Start new chats with a clean dashboard
- View all previous conversations in the sidebar
- Switch between different chat sessions
- Delete old conversations
- Automatically save chat progress

## Features

### 1. **New Chat Button**
- Click "➕ New chat" to start a fresh conversation
- Previous chat is automatically saved to history
- Main dashboard clears completely
- New session ID is generated

### 2. **Chat History Panel**
- Located in the left sidebar
- Shows up to 20 most recent chats
- Each chat displays:
  - Title (first user message, truncated)
  - Timestamp (date and time)
  - Delete button (🗑️)

### 3. **Chat Session Management**
- **Auto-save**: Every message is automatically saved
- **Persistent**: Chat history survives app restarts
- **Limit**: Keeps last 50 chats (older ones are removed)
- **Storage**: Saved in `chat_history.json`

### 4. **Load Previous Chats**
- Click any chat in history to reload it
- All messages are restored
- Document generation state is preserved
- Current chat is highlighted

### 5. **Delete Chats**
- Click 🗑️ button next to any chat
- Confirmation not required (instant delete)
- If deleting current chat, starts new one

## User Experience

### Starting Fresh
```
1. User clicks "➕ New chat"
2. Current chat saved to history
3. Dashboard clears
4. Ready for new conversation
```

### Quick Actions
```
1. User clicks "💍 Marriage Certificate"
2. Starts new chat automatically
3. Pre-fills with "Generate marriage certificate"
4. Begins document generation flow
```

### Continuing Previous Work
```
1. User sees chat titled "Generate marriage form..."
2. Clicks on it
3. All previous messages load
4. Can continue where they left off
```

## Technical Details

### Data Structure

Each chat session contains:
```json
{
  "id": "unique-uuid",
  "title": "First user message (truncated)",
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "timestamp": "2024-11-09T20:15:30",
  "session_data": {
    "collected_data": {...},
    "current_doc_type": "marriage",
    "current_state": "jaipur"
  }
}
```

### Storage

- **File**: `chat_history.json`
- **Location**: Root directory
- **Format**: JSON array of chat sessions
- **Encoding**: UTF-8 (supports all languages)

### Session State

Key session variables:
- `chat_history`: List of all saved chats
- `current_chat_id`: ID of active chat
- `chat_title`: Title of current chat
- `display_messages`: Messages shown in UI

## Benefits

### For Users
1. **Never Lose Work**: All conversations are saved
2. **Easy Navigation**: Quick access to previous chats
3. **Clean Interface**: Fresh start for each new task
4. **Context Switching**: Jump between different documents

### For System
1. **Better UX**: Matches familiar ChatGPT interface
2. **Data Persistence**: User history is preserved
3. **Debugging**: Can review past interactions
4. **Analytics**: Track usage patterns (future feature)

## Usage Examples

### Example 1: Multiple Documents
```
Session 1: "Generate marriage certificate for Jaipur"
→ Complete and download
→ Click "New chat"

Session 2: "Generate birth certificate for Delhi"
→ Complete and download
→ Click "New chat"

Session 3: "Generate income certificate"
→ In progress...

Sidebar shows:
- 💬 Generate income certificate (active)
- 💬 Generate birth certificate for Delhi
- 💬 Generate marriage certificate for Jaipur
```

### Example 2: Resume Later
```
Day 1:
- Start marriage certificate
- Provide groom details
- Close browser

Day 2:
- Open app
- Click on "Generate marriage certificate..." in history
- Continue from where left off
- Provide bride details
- Complete and download
```

### Example 3: Compare Documents
```
- Generate marriage cert for Jaipur
- Generate marriage cert for Delhi
- Switch between chats to compare
- See what fields were different
```

## Configuration

No configuration needed! The feature works out of the box.

Optional customization in code:
```python
# Maximum chats to keep
MAX_CHAT_HISTORY = 50  # Change in save_current_chat()

# Chats shown in sidebar
VISIBLE_CHATS = 20  # Change in render_sidebar()

# Title truncation length
TITLE_LENGTH = 50  # Change in save_current_chat()
```

## Privacy & Security

- **Local Storage**: All data stored locally on user's machine
- **No Cloud**: Chat history never leaves the device
- **User Control**: Users can delete any chat anytime
- **No Tracking**: No analytics or tracking of conversations

## Troubleshooting

### Chat History Not Showing
**Problem**: Sidebar shows "No chat history yet"

**Solution**:
- Start a conversation and send at least one message
- History appears after first interaction
- Check if `chat_history.json` exists

### Chat Not Saving
**Problem**: Messages disappear after refresh

**Solution**:
- Check file permissions for `chat_history.json`
- Ensure app has write access to directory
- Check logs for save errors

### Old Chats Not Loading
**Problem**: Clicking chat doesn't load messages

**Solution**:
- Check `chat_history.json` format is valid JSON
- Verify chat ID exists in history
- Try deleting corrupted chat

### Too Many Chats
**Problem**: Sidebar is cluttered

**Solution**:
- Delete old chats using 🗑️ button
- System auto-limits to 50 chats
- Oldest chats are removed automatically

## Future Enhancements

Potential improvements:
1. **Search**: Search through chat history
2. **Export**: Export chats to PDF/TXT
3. **Tags**: Tag chats by document type
4. **Favorites**: Star important chats
5. **Folders**: Organize chats into folders
6. **Sharing**: Share chat sessions (with privacy controls)

## Migration

If upgrading from old version:
- No migration needed
- Old sessions won't have history
- New chats will be saved automatically
- No data loss for current session
