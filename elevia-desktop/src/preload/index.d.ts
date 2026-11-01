import { ElectronAPI } from '@electron-toolkit/preload'
import { VocabularyRequest, VocabularyResponse } from './vocabulary'

declare global {
  interface Window {
    electron: ElectronAPI
    api: { vocabulary: (request: VocabularyRequest) => Promise<VocabularyResponse> }
  }
}
