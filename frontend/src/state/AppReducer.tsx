/*
* Defines a reducer function appStateReducer that manages application state based on various actions. 
* This function updates the state of the application according to the type of action, such as switching chat history, 
* updating the current chat, loading chat history, setting CosmosDB state, and more, ensuring the correct operation 
* and interaction of the application.
*/

import { Action, AppState } from './AppProvider'

// Define the reducer function appStateReducer that manages application state based on various actions
export const appStateReducer = (state: AppState, action: Action): AppState => {
  // Switch statement to handle different types of actions
  switch (action.type) {
    case 'TOGGLE_CHAT_HISTORY':
      return { ...state, isChatHistoryOpen: !state.isChatHistoryOpen }
    case 'UPDATE_CURRENT_CHAT':
      return { ...state, currentChat: action.payload }
    case 'UPDATE_CHAT_HISTORY_LOADING_STATE':
      return { ...state, chatHistoryLoadingState: action.payload }
    case 'UPDATE_CHAT_HISTORY':
      // If chatHistory or currentChat is not available, return the current state
      if (!state.chatHistory || !state.currentChat) {
        return state
      }
      // Find the index of the conversation in the chatHistory array
      const conversationIndex = state.chatHistory.findIndex(conv => conv.id === action.payload.id)
      // If the conversation exists in the chatHistory array, update the chatHistory with the new conversation
      if (conversationIndex !== -1) {
        const updatedChatHistory = [...state.chatHistory]
        updatedChatHistory[conversationIndex] = state.currentChat
        return { ...state, chatHistory: updatedChatHistory }
      // If the conversation does not exist in the chatHistory array, add the new conversation to the chatHistory
      } else {
        return { ...state, chatHistory: [...state.chatHistory, action.payload] }
      }
    case 'UPDATE_CHAT_TITLE':
      // If chatHistory is not available, return the current state
      if (!state.chatHistory) {
        return { ...state, chatHistory: [] }
      }
      // Update the title of the conversation in the chatHistory array
      const updatedChats = state.chatHistory.map(chat => {
        if (chat.id === action.payload.id) {
          if (state.currentChat?.id === action.payload.id) {
            state.currentChat.title = action.payload.title
          }
          //TODO: make api call to save new title to DB
          return { ...chat, title: action.payload.title }
        }
        return chat
      })
      return { ...state, chatHistory: updatedChats }
    case 'DELETE_CHAT_ENTRY':
      // If chatHistory is not available, return the current state
      if (!state.chatHistory) {
        return { ...state, chatHistory: [] }
      }
      const filteredChat = state.chatHistory.filter(chat => chat.id !== action.payload)
      state.currentChat = null
      //TODO: make api call to delete conversation from DB
      return { ...state, chatHistory: filteredChat }
    case 'DELETE_CHAT_HISTORY':
      //TODO: make api call to delete all conversations from DB
      return { ...state, chatHistory: [], filteredChatHistory: [], currentChat: null }
    case 'DELETE_CURRENT_CHAT_MESSAGES':
      //TODO: make api call to delete current conversation messages from DB
      // If currentChat or chatHistory is not available, return the current state
      if (!state.currentChat || !state.chatHistory) {
        return state
      }
      const updatedCurrentChat = {
        ...state.currentChat,
        messages: []
      }
      return {
        ...state,
        currentChat: updatedCurrentChat
      }
    case 'FETCH_CHAT_HISTORY':
      return { ...state, chatHistory: action.payload }
    case 'SET_COSMOSDB_STATUS':
      return { ...state, isCosmosDBAvailable: action.payload }
    case 'FETCH_FRONTEND_SETTINGS':
      return { ...state, isLoading: false, frontendSettings: action.payload }
    case 'SET_FEEDBACK_STATE':
      // Update the feedback state for the answer
      return {
        ...state,
        feedbackState: {
          ...state.feedbackState,
          [action.payload.answerId]: action.payload.feedback
        }
      }
    case 'SET_ANSWER_EXEC_RESULT':
      // Update the answer execution result for the answer
      return {
        ...state,
        answerExecResult: {
          ...state.answerExecResult,
          [action.payload.answerId]: action.payload.exec_result
        }
      }
    default:
      return state
  }
}
