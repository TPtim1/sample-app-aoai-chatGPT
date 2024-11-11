/* 
*  This component is responsible for rendering the chat history list.
*  It uses the ChatHistoryListItemGroups component to render the chat history list items.
*  It also uses the AppStateContext to access the chat history state.
*  The chat history is grouped by month and the most recent conversations are displayed first.
*  If there is no chat history, a message is displayed to indicate that there is no chat history.
*  The component is exported and rendered in the ChatHistory component.
*/

import React, { useContext } from 'react'
import { Stack, StackItem, Text } from '@fluentui/react'

import { Conversation } from '../../api/models'
import { AppStateContext } from '../../state/AppProvider'

import { ChatHistoryListItemGroups } from './ChatHistoryListItem'

interface ChatHistoryListProps {}

// Grouped chat history interface to group chat history by month and year and sort by date in descending order within each group of entries 
export interface GroupedChatHistory {
  month: string
  entries: Conversation[]
}

// Function to group chat history by month and year and sort by date in descending order within each group of entries
const groupByMonth = (entries: Conversation[]) => {
  const groups: GroupedChatHistory[] = [{ month: 'Recent', entries: [] }]
  const currentDate = new Date()

  // Iterate through each chat history entry and group by month and year
  entries.forEach(entry => {
    const date = new Date(entry.date)
    const daysDifference = (currentDate.getTime() - date.getTime()) / (1000 * 60 * 60 * 24)
    const monthYear = date.toLocaleString('default', { month: 'long', year: 'numeric' })
    const existingGroup = groups.find(group => group.month === monthYear)

    // Check if the chat history entry is within the last 7 days and group it as 'Recent'
    if (daysDifference <= 7) {
      groups[0].entries.push(entry)
    } else {
      if (existingGroup) {
        existingGroup.entries.push(entry)
      } else {
        groups.push({ month: monthYear, entries: [entry] })
      }
    }
  })

  // Sort the groups by date in descending order
  groups.sort((a, b) => {
    // Check if either group has no entries and handle it
    if (a.entries.length === 0 && b.entries.length === 0) {
      return 0 // No change in order
    } else if (a.entries.length === 0) {
      return 1 // Move 'a' to a higher index (bottom)
    } else if (b.entries.length === 0) {
      return -1 // Move 'b' to a higher index (bottom)
    }
    const dateA = new Date(a.entries[0].date)
    const dateB = new Date(b.entries[0].date)
    return dateB.getTime() - dateA.getTime()
  })

  groups.forEach(group => {
    group.entries.sort((a, b) => {
      const dateA = new Date(a.date)
      const dateB = new Date(b.date)
      return dateB.getTime() - dateA.getTime()
    })
  })

  return groups
}

// ChatHistoryList component to render the chat history list items 
const ChatHistoryList: React.FC<ChatHistoryListProps> = () => {
  // Access the chat history state from the AppStateContext 
  const appStateContext = useContext(AppStateContext)
  const chatHistory = appStateContext?.state.chatHistory

  // React hook to update the component when the chat history state changes
  React.useEffect(() => {}, [appStateContext?.state.chatHistory])

  let groupedChatHistory
  if (chatHistory && chatHistory.length > 0) {
    groupedChatHistory = groupByMonth(chatHistory)
  } else {
    return (
      <Stack horizontal horizontalAlign="center" verticalAlign="center" style={{ width: '100%', marginTop: 10 }}>
        <StackItem>
          <Text style={{ alignSelf: 'center', fontWeight: '400', fontSize: 14 }}>
            <span>No chat history.</span>
          </Text>
        </StackItem>
      </Stack>
    )
  }

  return <ChatHistoryListItemGroups groupedChatHistory={groupedChatHistory} />
}

export default ChatHistoryList
