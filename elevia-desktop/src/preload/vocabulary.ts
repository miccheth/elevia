export interface VocabularyItem {
  id: number
  tagId: number
  parentId: number | null
  name: string
}

export type VocabularyRequest =
  | { action: 'list' }
  | { action: 'create'; name: string; parentId: number | null }
  | { action: 'rename'; tagId: number; name: string }
  | { action: 'delete'; placementId: number }

export interface VocabularyResponse {
  items?: VocabularyItem[]
  error?: string
}
