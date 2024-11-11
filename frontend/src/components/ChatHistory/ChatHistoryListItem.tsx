/* 
* This component is responsible for rendering a single chat history item in the chat history list.
* It also contains the logic for deleting and renaming chat history items.
*/

import * as React from 'react'
import { useContext, useEffect, useRef, useState } from 'react'
import {
  DefaultButton,
  Dialog,
  DialogFooter,
  DialogType,
  IconButton,
  ITextField,
  List,
  PrimaryButton,
  Separator,
  Spinner,
  SpinnerSize,
  Stack,
  Text,
  TextField
} from '@fluentui/react'
import { useBoolean } from '@fluentui/react-hooks'

import { historyDelete, historyList, historyRename } from '../../api'
import { Conversation } from '../../api/models'
import { AppStateContext } from '../../state/AppProvider'

import { GroupedChatHistory } from './ChatHistoryList'

// Import the styles for the ChatHistoryListItem component
import styles from './ChatHistoryPanel.module.css'

// Define the props for the ChatHistoryListItemCell component
interface ChatHistoryListItemCellProps {
  item?: Conversation
  onSelect: (item: Conversation | null) => void
}

// Define the props for the ChatHistoryListItemGroups component
interface ChatHistoryListItemGroupsProps {
  groupedChatHistory: GroupedChatHistory[]
}

// Function to format the month name based on the current year
const formatMonth = (month: string) => {
  const currentDate = new Date()
  const currentYear = currentDate.getFullYear()

  const [monthName, yearString] = month.split(' ')
  const year = parseInt(yearString)

  if (year === currentYear) {
    return monthName
  } else {
    return month
  }
}

// ChatHistoryListItemCell component to render a single chat history item in the chat history list with delete and rename functionality
export const ChatHistoryListItemCell: React.FC<ChatHistoryListItemCellProps> = ({ item, onSelect }) => {
  const [isHovered, setIsHovered] = React.useState(false)
  const [edit, setEdit] = useState(false)
  const [editTitle, setEditTitle] = useState('')
  const [hideDeleteDialog, { toggle: toggleDeleteDialog }] = useBoolean(true)
  const [errorDelete, setErrorDelete] = useState(false)
  const [renameLoading, setRenameLoading] = useState(false)
  const [errorRename, setErrorRename] = useState<string | undefined>(undefined)
  const [textFieldFocused, setTextFieldFocused] = useState(false)
  const textFieldRef = useRef<ITextField | null>(null)

  const appStateContext = React.useContext(AppStateContext)
  const isSelected = item?.id === appStateContext?.state.currentChat?.id
  const dialogContentProps = {
    type: DialogType.close,
    title: 'Are you sure you want to delete this item?',
    closeButtonAriaLabel: 'Close',
    subText: 'The history of this chat session will permanently removed.'
  }

  const modalProps = {
    titleAriaId: 'labelId',
    subtitleAriaId: 'subTextId',
    isBlocking: true,
    styles: { main: { maxWidth: 450 } }
  }

  if (!item) {
    return null
  }

  // Focus on the text field when editing the chat history item title
  useEffect(() => {
    if (textFieldFocused && textFieldRef.current) {
      textFieldRef.current.focus()
      setTextFieldFocused(false)
    }
  }, [textFieldFocused])

  // Reset the edit state when the current chat changes
  useEffect(() => {
    if (appStateContext?.state.currentChat?.id !== item?.id) {
      setEdit(false)
      setEditTitle('')
    }
  }, [appStateContext?.state.currentChat?.id, item?.id])

  // Reset the edit state when the chat history item changes
  const onDelete = async () => {
    const response = await historyDelete(item.id)
    if (!response.ok) {
      setErrorDelete(true)
      setTimeout(() => {
        setErrorDelete(false)
      }, 5000)
    } else {
      appStateContext?.dispatch({ type: 'DELETE_CHAT_ENTRY', payload: item.id })
    }
    toggleDeleteDialog()
  }

  // Set the edit state to true when the user clicks the edit button
  const onEdit = () => {
    setEdit(true)
    setTextFieldFocused(true)
    setEditTitle(item?.title)
  }

  // Handle the selection of a chat history item
  const handleSelectItem = () => {
    onSelect(item)
    appStateContext?.dispatch({ type: 'UPDATE_CURRENT_CHAT', payload: item })
  }

  // Truncate the chat history item title if it is longer than 28 characters
  const truncatedTitle = item?.title?.length > 28 ? `${item.title.substring(0, 28)} ...` : item.title

  // Save the edited chat history item title and update the chat history item in the state 
  const handleSaveEdit = async (e: any) => {
    e.preventDefault()
    if (errorRename || renameLoading) {
      return
    }
    if (editTitle == item.title) {
      setErrorRename('Error: Enter a new title to proceed.')
      setTimeout(() => {
        setErrorRename(undefined)
        setTextFieldFocused(true)
        if (textFieldRef.current) {
          textFieldRef.current.focus()
        }
      }, 5000)
      return
    }
    setRenameLoading(true)
    const response = await historyRename(item.id, editTitle)
    if (!response.ok) {
      setErrorRename('Error: could not rename item')
      setTimeout(() => {
        setTextFieldFocused(true)
        setErrorRename(undefined)
        if (textFieldRef.current) {
          textFieldRef.current.focus()
        }
      }, 5000)
    } else {
      setRenameLoading(false)
      setEdit(false)
      appStateContext?.dispatch({ type: 'UPDATE_CHAT_TITLE', payload: { ...item, title: editTitle } as Conversation })
      setEditTitle('')
    }
  }

  // Update the chat history item title when the user types in the text field
  const chatHistoryTitleOnChange = (e: any) => {
    setEditTitle(e.target.value)
  }

  // Cancel the edit state and reset the chat history item title
  const cancelEditTitle = () => {
    setEdit(false)
    setEditTitle('')
  }

  // Handle key press events for the chat history item title
  const handleKeyPressEdit = (e: any) => {
    if (e.key === 'Enter') {
      return handleSaveEdit(e)
    }
    if (e.key === 'Escape') {
      cancelEditTitle()
      return
    }
  }

  return (
    <Stack
      key={item.id}
      tabIndex={0}
      aria-label="chat history item"
      className={styles.itemCell}
      onClick={() => handleSelectItem()}
      onKeyDown={e => (e.key === 'Enter' || e.key === ' ' ? handleSelectItem() : null)}
      verticalAlign="center"
      // horizontal
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      styles={{
        root: {
          backgroundColor: isSelected ? '#e6e6e6' : 'transparent'
        }
      }}>
      {edit ? (
        <>
          {/* Edit title form */}
          <Stack.Item style={{ width: '100%' }}>
            <form aria-label="edit title form" onSubmit={e => handleSaveEdit(e)} style={{ padding: '5px 0px' }}>
              <Stack horizontal verticalAlign={'start'}>
                {/* Text field to edit the chat history item title */}
                <Stack.Item>
                  <TextField
                    componentRef={textFieldRef}
                    autoFocus={textFieldFocused}
                    value={editTitle}
                    placeholder={item.title}
                    onChange={chatHistoryTitleOnChange}
                    onKeyDown={handleKeyPressEdit}
                    // errorMessage={errorRename}
                    disabled={errorRename ? true : false}
                  />
                {/* Action buttons to save or cancel the edit */}
                </Stack.Item>
                {editTitle && (
                  <Stack.Item>
                    <Stack aria-label="action button group" horizontal verticalAlign={'center'}>
                      {/* Save edit button */}
                      <IconButton
                        role="button"
                        disabled={errorRename !== undefined}
                        onKeyDown={e => (e.key === ' ' || e.key === 'Enter' ? handleSaveEdit(e) : null)}
                        onClick={e => handleSaveEdit(e)}
                        aria-label="confirm new title"
                        iconProps={{ iconName: 'CheckMark' }}
                        styles={{ root: { color: 'green', marginLeft: '5px' } }}
                      />
                      {/* Cancel edit button */}
                      <IconButton
                        role="button"
                        disabled={errorRename !== undefined}
                        onKeyDown={e => (e.key === ' ' || e.key === 'Enter' ? cancelEditTitle() : null)}
                        onClick={() => cancelEditTitle()}
                        aria-label="cancel edit title"
                        iconProps={{ iconName: 'Cancel' }}
                        styles={{ root: { color: 'red', marginLeft: '5px' } }}
                      />
                    </Stack>
                  </Stack.Item>
                )}
              </Stack>
              {errorRename && (
                <Text
                  role="alert"
                  aria-label={errorRename}
                  style={{ fontSize: 12, fontWeight: 400, color: 'rgb(164,38,44)' }}>
                  {errorRename}
                </Text>
              )}
            </form>
          </Stack.Item>
        </>
      ) : (
        <>
          {/* Chat history item title */}
          <Stack horizontal verticalAlign={'center'} style={{ width: '100%' }}>
            <div className={styles.chatTitle}>{truncatedTitle}</div>
            {(isSelected || isHovered) && (
              <Stack horizontal horizontalAlign="end">
                {/* Action buttons to delete or edit the chat history item */}
                <IconButton
                  className={styles.itemButton}
                  iconProps={{ iconName: 'Delete' }}
                  title="Delete"
                  onClick={toggleDeleteDialog}
                  onKeyDown={e => (e.key === ' ' ? toggleDeleteDialog() : null)}
                />
                {/* Edit button */}
                <IconButton
                  className={styles.itemButton}
                  iconProps={{ iconName: 'Edit' }}
                  title="Edit"
                  onClick={onEdit}
                  onKeyDown={e => (e.key === ' ' ? onEdit() : null)}
                />
              </Stack>
            )}
          </Stack>
        </>
      )}
      {errorDelete && (
        <Text
          styles={{
            root: { color: 'red', marginTop: 5, fontSize: 14 }
          }}>
          Error: could not delete item
        </Text>
      )}
      {/* Delete dialog */}
      <Dialog
        hidden={hideDeleteDialog}
        onDismiss={toggleDeleteDialog}
        dialogContentProps={dialogContentProps}
        modalProps={modalProps}>
        <DialogFooter>
          <PrimaryButton onClick={onDelete} text="Delete" />
          <DefaultButton onClick={toggleDeleteDialog} text="Cancel" />
        </DialogFooter>
      </Dialog>
    </Stack>
  )
}

// ChatHistoryListItemGroups component to render the chat history list items grouped by month and year 
export const ChatHistoryListItemGroups: React.FC<ChatHistoryListItemGroupsProps> = ({ groupedChatHistory }) => {
  const appStateContext = useContext(AppStateContext)
  const observerTarget = useRef(null)
  const [, setSelectedItem] = React.useState<Conversation | null>(null)
  const [offset, setOffset] = useState<number>(25)
  const [observerCounter, setObserverCounter] = useState(0)
  const [showSpinner, setShowSpinner] = useState(false)
  const firstRender = useRef(true)

  // Handle the selection of a chat history item
  const handleSelectHistory = (item?: Conversation) => {
    if (item) {
      setSelectedItem(item)
    }
  }

  // Render the chat history list items
  const onRenderCell = (item?: Conversation) => {
    return <ChatHistoryListItemCell item={item} onSelect={() => handleSelectHistory(item)} />
  }

  // Fetch more chat history when the observer target is in view
  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false
      return
    }
    handleFetchHistory()
    setOffset(offset => (offset += 25))
  }, [observerCounter])

  // Fetch the chat history from the API
  const handleFetchHistory = async () => {
    // Access the chat history state from the AppStateContext
    const currentChatHistory = appStateContext?.state.chatHistory
    setShowSpinner(true)

    // Fetch the chat history from the API
    await historyList(offset).then(response => {
      const concatenatedChatHistory = currentChatHistory && response && currentChatHistory.concat(...response)
      if (response) {
        appStateContext?.dispatch({ type: 'FETCH_CHAT_HISTORY', payload: concatenatedChatHistory || response })
      } else {
        appStateContext?.dispatch({ type: 'FETCH_CHAT_HISTORY', payload: null })
      }
      setShowSpinner(false)
      return response
    })
  }

  // Create an observer to fetch more chat history when the observer target is in view
  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting) setObserverCounter(observerCounter => (observerCounter += 1))
      },
      { threshold: 1 }
    )

    // Observe the observer target
    if (observerTarget.current) observer.observe(observerTarget.current)

    // Unobserve the observer target when the component is unmounted
    return () => {
      if (observerTarget.current) observer.unobserve(observerTarget.current)
    }
  }, [observerTarget])

  return (
    // Render the chat history list items grouped by month and year
    <div className={styles.listContainer} data-is-scrollable>
      {groupedChatHistory.map(
        group =>
          group.entries.length > 0 && (
            <Stack
              horizontalAlign="start"
              verticalAlign="center"
              key={group.month}
              className={styles.chatGroup}
              aria-label={`chat history group: ${group.month}`}>
              <Stack aria-label={group.month} className={styles.chatMonth}>
                {formatMonth(group.month)}
              </Stack>
              <List
                aria-label={`chat history list`}
                items={group.entries}
                onRenderCell={onRenderCell}
                className={styles.chatList}
              />
              {/* Observer target to fetch more chat history */}
              <div ref={observerTarget} />
              <Separator
                styles={{
                  root: {
                    width: '100%',
                    position: 'relative',
                    '::before': {
                      backgroundColor: '#d6d6d6'
                    }
                  }
                }}
              />
            </Stack>
          )
      )}
      {/* Spinner to indicate that more chat history is being loaded */}
      {showSpinner && (
        <div className={styles.spinnerContainer}>
          <Spinner size={SpinnerSize.small} aria-label="loading more chat history" className={styles.spinner} />
        </div>
      )}
    </div>
  )
}
