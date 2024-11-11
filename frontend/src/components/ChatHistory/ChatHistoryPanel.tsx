/* 
* Component for displaying chat history panel
* It uses the application context to get the chat history status, allows the user to show 
* or hide the chat history, displays the chat history loading status, and provides an option 
* to clear the entire chat history using a dialog box.
*/

import { useContext } from 'react'
import React from 'react'
import {
  CommandBarButton,
  ContextualMenu,
  DefaultButton,
  Dialog,
  DialogFooter,
  DialogType,
  ICommandBarStyles,
  IContextualMenuItem,
  IStackStyles,
  PrimaryButton,
  Spinner,
  SpinnerSize,
  Stack,
  StackItem,
  Text
} from '@fluentui/react'
import { useBoolean } from '@fluentui/react-hooks'

import { ChatHistoryLoadingState, historyDeleteAll } from '../../api'
import { AppStateContext } from '../../state/AppProvider'

import ChatHistoryList from './ChatHistoryList'

// Import styles
import styles from './ChatHistoryPanel.module.css'

// Define the ChatHistoryPanelProps interface
interface ChatHistoryPanelProps {}

// Define the ChatHistoryPanelTabs enum
export enum ChatHistoryPanelTabs {
  History = 'History'
}

// Define the commandBarStyle and commandBarButtonStyle variables
const commandBarStyle: ICommandBarStyles = {
  root: {
    padding: '0',
    display: 'flex',
    justifyContent: 'center',
    backgroundColor: 'transparent'
  }
}

// Define the commandBarButtonStyle variable
const commandBarButtonStyle: Partial<IStackStyles> = { root: { height: '50px' } }

// Define the ChatHistoryPanel functional component
export function ChatHistoryPanel(_props: ChatHistoryPanelProps) {
  const appStateContext = useContext(AppStateContext)
  const [showContextualMenu, setShowContextualMenu] = React.useState(false)
  const [hideClearAllDialog, { toggle: toggleClearAllDialog }] = useBoolean(true)
  const [clearing, setClearing] = React.useState(false)
  const [clearingError, setClearingError] = React.useState(false)

  // Define the clearAllDialogContentProps and modalProps variables
  const clearAllDialogContentProps = {
    type: DialogType.close,
    title: !clearingError ? 'Are you sure you want to clear all chat history?' : 'Error deleting all of chat history',
    closeButtonAriaLabel: 'Close',
    subText: !clearingError
      ? 'All chat history will be permanently removed.'
      : 'Please try again. If the problem persists, please contact the site administrator.'
  }

  // Define the modalProps variable with the titleAriaId, subtitleAriaId, isBlocking, and styles properties
  const modalProps = {
    titleAriaId: 'labelId',
    subtitleAriaId: 'subTextId',
    isBlocking: true,
    styles: { main: { maxWidth: 450 } }
  }

  // Define the menuItems variable with the clearAll item
  const menuItems: IContextualMenuItem[] = [
    { key: 'clearAll', text: 'Clear all chat history', iconProps: { iconName: 'Delete' } }
  ]

  // Define the handleHistoryClick function that toggles the chat history
  const handleHistoryClick = () => {
    appStateContext?.dispatch({ type: 'TOGGLE_CHAT_HISTORY' })
  }

  // Define the onShowContextualMenu and onHideContextualMenu functions
  const onShowContextualMenu = React.useCallback((ev: React.MouseEvent<HTMLElement>) => {
    ev.preventDefault() // don't navigate
    setShowContextualMenu(true)
  }, [])

  // Define the onHideContextualMenu function
  const onHideContextualMenu = React.useCallback(() => setShowContextualMenu(false), [])

  // Define the onClearAllChatHistory, onHideClearAllDialog, and onClearAllDialog functions
  const onClearAllChatHistory = async () => {
    setClearing(true)
    const response = await historyDeleteAll()
    if (!response.ok) {
      setClearingError(true)
    } else {
      appStateContext?.dispatch({ type: 'DELETE_CHAT_HISTORY' })
      toggleClearAllDialog()
    }
    setClearing(false)
  }

  const onHideClearAllDialog = () => {
    toggleClearAllDialog()
    setTimeout(() => {
      setClearingError(false)
    }, 2000)
  }

  React.useEffect(() => {}, [appStateContext?.state.chatHistory, clearingError])

  return (
    <section className={styles.container} data-is-scrollable aria-label={'chat history panel'}>
      <Stack horizontal horizontalAlign="space-between" verticalAlign="center" wrap aria-label="chat history header">
        {/* Chat history header */}
        <StackItem>
          <Text
            role="heading"
            aria-level={2}
            style={{
              alignSelf: 'center',
              fontWeight: '600',
              fontSize: '18px',
              marginRight: 'auto',
              paddingLeft: '20px'
            }}>
            Chat history
          </Text>
        </StackItem>
        {/* Chat history header buttons */}
        <Stack verticalAlign="start">
          <Stack horizontal styles={commandBarButtonStyle}>
            {/* Clear all chat history button */}
            <CommandBarButton
              iconProps={{ iconName: 'More' }}
              title={'Clear all chat history'}
              onClick={onShowContextualMenu}
              aria-label={'clear all chat history'}
              styles={commandBarStyle}
              role="button"
              id="moreButton"
            />
            {/* Contextual menu */}
            <ContextualMenu
              items={menuItems}
              hidden={!showContextualMenu}
              target={'#moreButton'}
              onItemClick={toggleClearAllDialog}
              onDismiss={onHideContextualMenu}
            />
            {/* Hide chat history button */}
            <CommandBarButton
              iconProps={{ iconName: 'Cancel' }}
              title={'Hide'}
              onClick={handleHistoryClick}
              aria-label={'hide button'}
              styles={commandBarStyle}
              role="button"
            />
          </Stack>
        </Stack>
      </Stack>
      {/* Chat history panel content */}
      <Stack
        aria-label="chat history panel content"
        styles={{
          root: {
            display: 'flex',
            flexGrow: 1,
            flexDirection: 'column',
            paddingTop: '2.5px',
            maxWidth: '100%'
          }
        }}
        style={{
          display: 'flex',
          flexGrow: 1,
          flexDirection: 'column',
          flexWrap: 'wrap',
          padding: '1px'
        }}>
        {/* Chat history list container */}
        <Stack className={styles.chatHistoryListContainer}>
          {appStateContext?.state.chatHistoryLoadingState === ChatHistoryLoadingState.Success &&
            appStateContext?.state.isCosmosDBAvailable.cosmosDB && <ChatHistoryList />}
          {appStateContext?.state.chatHistoryLoadingState === ChatHistoryLoadingState.Fail &&
            appStateContext?.state.isCosmosDBAvailable && (
              <>
                <Stack>
                  <Stack horizontalAlign="center" verticalAlign="center" style={{ width: '100%', marginTop: 10 }}>
                    {/* Chat history error message */}
                    <StackItem>
                      <Text style={{ alignSelf: 'center', fontWeight: '400', fontSize: 16 }}>
                        {appStateContext?.state.isCosmosDBAvailable?.status && (
                          <span>{appStateContext?.state.isCosmosDBAvailable?.status}</span>
                        )}
                        {!appStateContext?.state.isCosmosDBAvailable?.status && <span>Error loading chat history</span>}
                      </Text>
                    </StackItem>
                    <StackItem>
                      <Text style={{ alignSelf: 'center', fontWeight: '400', fontSize: 14 }}>
                        <span>Chat history can't be saved at this time</span>
                      </Text>
                    </StackItem>
                  </Stack>
                </Stack>
              </>
            )}
          {appStateContext?.state.chatHistoryLoadingState === ChatHistoryLoadingState.Loading && (
            <>
              <Stack>
                <Stack
                  horizontal
                  horizontalAlign="center"
                  verticalAlign="center"
                  style={{ width: '100%', marginTop: 10 }}>
                  {/* Chat history loading spinner */}
                  <StackItem style={{ justifyContent: 'center', alignItems: 'center' }}>
                    <Spinner
                      style={{ alignSelf: 'flex-start', height: '100%', marginRight: '5px' }}
                      size={SpinnerSize.medium}
                    />
                  </StackItem>
                  {/* Chat history loading message */}
                  <StackItem>
                    <Text style={{ alignSelf: 'center', fontWeight: '400', fontSize: 14 }}>
                      <span style={{ whiteSpace: 'pre-wrap' }}>Loading chat history</span>
                    </Text>
                  </StackItem>
                </Stack>
              </Stack>
            </>
          )}
        </Stack>
      </Stack>
      {/* Clear all chat history dialog */}
      <Dialog
        hidden={hideClearAllDialog}
        onDismiss={clearing ? () => {} : onHideClearAllDialog}
        dialogContentProps={clearAllDialogContentProps}
        modalProps={modalProps}>
        <DialogFooter>
          {!clearingError && <PrimaryButton onClick={onClearAllChatHistory} disabled={clearing} text="Clear All" />}
          <DefaultButton
            onClick={onHideClearAllDialog}
            disabled={clearing}
            text={!clearingError ? 'Cancel' : 'Close'}
          />
        </DialogFooter>
      </Dialog>
    </section>
  )
}
