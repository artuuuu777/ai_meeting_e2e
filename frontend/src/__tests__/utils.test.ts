import { formatDuration, formatFileSize, formatRelativeTime } from '@/lib/utils'

describe('Utils', () => {
  describe('formatDuration', () => {
    it('formats seconds correctly', () => {
      expect(formatDuration(30)).toBe('0:30')
      expect(formatDuration(90)).toBe('1:30')
      expect(formatDuration(3661)).toBe('1:01:01')
    })

    it('handles edge cases', () => {
      expect(formatDuration(0)).toBe('0:00')
      expect(formatDuration(3600)).toBe('1:00:00')
    })
  })

  describe('formatFileSize', () => {
    it('formats bytes correctly', () => {
      expect(formatFileSize(0)).toBe('0 Bytes')
      expect(formatFileSize(1024)).toBe('1 KB')
      expect(formatFileSize(1048576)).toBe('1 MB')
      expect(formatFileSize(1073741824)).toBe('1 GB')
    })

    it('handles decimal places', () => {
      expect(formatFileSize(1536)).toBe('1.5 KB')
      expect(formatFileSize(1610612736)).toBe('1.5 GB')
    })
  })

  describe('formatRelativeTime', () => {
    beforeEach(() => {
      jest.useFakeTimers()
      jest.setSystemTime(new Date('2024-01-15T12:00:00Z'))
    })

    afterEach(() => {
      jest.useRealTimers()
    })

    it('formats recent times correctly', () => {
      const now = new Date('2024-01-15T12:00:00Z')
      const thirtySecondsAgo = new Date('2024-01-15T11:59:30Z')
      const twoMinutesAgo = new Date('2024-01-15T11:58:00Z')
      const twoHoursAgo = new Date('2024-01-15T10:00:00Z')
      const twoDaysAgo = new Date('2024-01-13T12:00:00Z')

      expect(formatRelativeTime(thirtySecondsAgo)).toBe('just now')
      expect(formatRelativeTime(twoMinutesAgo)).toBe('2m ago')
      expect(formatRelativeTime(twoHoursAgo)).toBe('2h ago')
      expect(formatRelativeTime(twoDaysAgo)).toBe('2d ago')
    })

    it('formats old dates as locale string', () => {
      const oldDate = new Date('2023-01-15T12:00:00Z')
      expect(formatRelativeTime(oldDate)).toBe(oldDate.toLocaleDateString())
    })
  })
})