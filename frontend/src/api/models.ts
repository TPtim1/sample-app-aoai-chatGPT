/*
* This file contains the typescript models for the API responses.
* These models are used to define the structure of the data that is returned by the API.
* This is useful when we want to define the structure of the data that is returned by the API
* so that we can use it in our frontend code.
* This is often used to create a single entry point for multiple modules,
* making it easier to import them elsewhere in the application.
*/


//Typ pre odpoveď na otázku, obsahuje odpoveď, citácie, generovaný graf, prípadnú chybu, 
//ID správy, spätnú väzbu a výsledky vykonania.
export type AskResponse = {
  answer: string | []
  citations: Citation[]
  generated_chart: string | null
  error?: string
  message_id?: string
  feedback?: Feedback
  exec_results?: ExecResults[]
}

//Typ pre citáciu, obsahuje index časti, obsah, ID, názov, cestu k súboru, URL, metadáta, 
//ID časti a ID reindexácie.
export type Citation = {
  part_index?: number
  content: string
  id: string
  title: string | null
  filepath: string | null
  url: string | null
  metadata: string | null
  chunk_id: string | null
  reindex_id: string | null
}

//Typ pre obsah správy nástroja, obsahuje citácie a zámer.
export type ToolMessageContent = {
  citations: Citation[]
  intent: string
}

//Typ pre výsledok vykonania na Azure SQL Serveri, obsahuje zámer, vyhľadávací dotaz, 
//výsledok vyhľadávania, generovaný kód a výsledok vykonania kódu.
export type AzureSqlServerExecResult = {
  intent: string
  search_query: string | null
  search_result: string | null
  code_generated: string | null
  code_exec_result?: string | undefined
}

//Typ pre všetky výsledky vykonania na Azure SQL Serveri, obsahuje pole výsledkov.
export type AzureSqlServerExecResults = {
  all_exec_results: AzureSqlServerExecResult[]
}

//Typ pre správu v chate, obsahuje ID, rolu, obsah, prípadné ukončenie, dátum, spätnú väzbu a kontext.
export type ChatMessage = {
  id: string
  role: string
  content: string | [{ type: string; text: string }, { type: string; image_url: { url: string } }]
  end_turn?: boolean
  date: string
  feedback?: Feedback
  context?: string
}

//Typ pre výsledky vykonania, obsahuje zámer, vyhľadávací dotaz, výsledok vyhľadávania a generovaný kód.
export type ExecResults = {
  intent: string
  search_query: string | null
  search_result: string | null
  code_generated: string | null
}

//Typ pre konverzáciu, obsahuje ID, názov, správy a dátum.
export type Conversation = {
  id: string
  title: string
  messages: ChatMessage[]
  date: string
}

//Enumerácia pre typ dokončenia chatu, obsahuje hodnoty ChatCompletion a ChatCompletionChunk.
export enum ChatCompletionType {
  ChatCompletion = 'chat.completion',
  ChatCompletionChunk = 'chat.completion.chunk'
}

//Typ pre výber odpovede v chate, obsahuje správy.
export type ChatResponseChoice = {
  messages: ChatMessage[]
}

//Typ pre odpoveď v chate, obsahuje ID, model, čas vytvorenia, objekt typu dokončenia chatu, 
//výbery odpovedí, metadáta histórie a prípadnú chybu.
export type ChatResponse = {
  id: string
  model: string
  created: number
  object: ChatCompletionType
  choices: ChatResponseChoice[]
  history_metadata: {
    conversation_id: string
    title: string
    date: string
  }
  error?: any
}

//Typ pre požiadavku na konverzáciu, obsahuje správy.
export type ConversationRequest = {
  messages: ChatMessage[]
}

//Typ pre informácie o používateľovi, obsahuje prístupový token, čas vypršania, 
//ID token, názov poskytovateľa, nároky používateľa a ID používateľa.
export type UserInfo = {
  access_token: string
  expires_on: string
  id_token: string
  provider_name: string
  user_claims: any[]
  user_id: string
}

//Enumerácia pre stav CosmosDB, obsahuje rôzne stavy ako NotConfigured, NotWorking, InvalidCredentials, 
//InvalidDatabase, InvalidContainer a Working.
export enum CosmosDBStatus {
  NotConfigured = 'CosmosDB is not configured',
  NotWorking = 'CosmosDB is not working',
  InvalidCredentials = 'CosmosDB has invalid credentials',
  InvalidDatabase = 'Invalid CosmosDB database name',
  InvalidContainer = 'Invalid CosmosDB container name',
  Working = 'CosmosDB is configured and working'
}

//Typ pre zdravie CosmosDB, obsahuje boolean pre CosmosDB a stav.
export type CosmosDBHealth = {
  cosmosDB: boolean
  status: string
}

//Enumerácia pre stav načítania histórie chatu, obsahuje hodnoty Loading, Success, Fail a NotStarted.
export enum ChatHistoryLoadingState {
  Loading = 'loading',
  Success = 'success',
  Fail = 'fail',
  NotStarted = 'notStarted'
}

//Typ pre chybovú správu, obsahuje názov a podnadpis.
export type ErrorMessage = {
  title: string
  subtitle: string
}

//Typ pre nastavenia používateľského rozhrania, obsahuje názov, názov chatu, popis chatu, logo, 
//logo chatu, zobrazenie tlačidla zdieľania a zobrazenie tlačidla histórie chatu.
export type UI = {
  title: string
  chat_title: string
  chat_description: string
  logo?: string
  chat_logo?: string
  show_share_button?: boolean
  show_chat_history_button?: boolean
}

//Typ pre nastavenia frontendu, obsahuje povolenie autentifikácie, povolenie spätnej väzby, 
//používateľské rozhranie, sanitizáciu odpovede a povolenie OYD.
export type FrontendSettings = {
  auth_enabled?: string | null
  feedback_enabled?: string | null
  ui?: UI
  sanitize_answer?: boolean
  oyd_enabled?: boolean
}

//Enumerácia pre spätnú väzbu, obsahuje rôzne hodnoty ako Neutral, Positive, Negative, 
//MissingCitation, WrongCitation, OutOfScope, InaccurateOrIrrelevant, OtherUnhelpful, 
//HateSpeech, Violent, Sexual, Manipulative a OtherHarmful.
export enum Feedback {
  Neutral = 'neutral',
  Positive = 'positive',
  Negative = 'negative',
  MissingCitation = 'missing_citation',
  WrongCitation = 'wrong_citation',
  OutOfScope = 'out_of_scope',
  InaccurateOrIrrelevant = 'inaccurate_or_irrelevant',
  OtherUnhelpful = 'other_unhelpful',
  HateSpeech = 'hate_speech',
  Violent = 'violent',
  Sexual = 'sexual',
  Manipulative = 'manipulative',
  OtherHarmful = 'other_harmlful'
}
