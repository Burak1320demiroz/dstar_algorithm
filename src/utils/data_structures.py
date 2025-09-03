import heapq
from typing import Any, List, Tuple, Dict

class PriorityQueue:
    """Priority queue implementasyonu"""
    
    def __init__(self):
        self.elements = []
        self.entry_finder = {}
        self.counter = 0
        self.REMOVED = '<removed-task>'
    
    def insert(self, item: Any, priority: Tuple[float, float]):
        """Öğe ekle"""
        if item in self.entry_finder:
            self.remove(item)
        
        count = self.counter
        self.counter += 1
        entry = [priority, count, item]
        self.entry_finder[item] = entry
        heapq.heappush(self.elements, entry)
    
    def remove(self, item: Any):
        """Öğeyi kaldır"""
        if item in self.entry_finder:
            entry = self.entry_finder.pop(item)
            entry[-1] = self.REMOVED
    
    def pop(self) -> Any:
        """En yüksek öncelikli öğeyi çıkar"""
        while self.elements:
            priority, count, item = heapq.heappop(self.elements)
            if item is not self.REMOVED:
                del self.entry_finder[item]
                return item
        raise KeyError('pop from empty priority queue')
    
    def top_key(self) -> Tuple[float, float]:
        """En üstteki öğenin önceliğini getir"""
        while self.elements:
            priority, count, item = self.elements[0]
            if item is not self.REMOVED:
                return priority
            heapq.heappop(self.elements)
        return (float('inf'), float('inf'))
    
    def contains(self, item: Any) -> bool:
        """Öğe var mı kontrol et"""
        return item in self.entry_finder
    
    def empty(self) -> bool:
        """Boş mu kontrol et"""
        return not bool(self.entry_finder)
    
    def clear(self):
        """Temizle"""
        self.elements.clear()
        self.entry_finder.clear()
        self.counter = 0