#!/usr/bin/env python3
"""LeetCode-Style Python Interview Questions Generator"""

def generate_leetcode_questions():
    """Generate LeetCode-style coding problems with solutions."""
    
    questions = [
        {
            'title': 'Two Sum',
            'difficulty': 'Easy',
            'problem': '''Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

Example 1:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].

Constraints:
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- -10^9 <= target <= 10^9
''',
            'solution': '''class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # Use a hash map to store value -> index mapping
        seen = {}
        
        for i, num in enumerate(nums):
            complement = target - num
            
            if complement in seen:
                return [seen[complement], i]
            
            seen[num] = i
        
        # This should never be reached given problem constraints
        return []

# Time Complexity: O(n)
# Space Complexity: O(n)''',
            'key_concepts': ['Hash Map', 'Two Pointers', 'Array']
        },
        {
            'title': 'Valid Parentheses',
            'difficulty': 'Easy',
            'problem': '''Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.

An input string is valid if:
- Open brackets must be closed by the same type of brackets.
- Open brackets must be closed in the correct order.
- Every close bracket has a corresponding open bracket of the same type.

Example 1:
Input: s = "()"
Output: true

Example 2:
Input: s = "()[]{}"
Output: true

Example 3:
Input: s = "(]"
Output: false

Constraints:
- 1 <= s.length <= 10^4
- s consists of parentheses only '()[]{}'.
''',
            'solution': '''class Solution:
    def isValid(self, s: str) -> bool:
        # Stack to track opening brackets
        stack = []
        
        # Mapping of closing to opening brackets
        bracket_map = {')': '(', '}': '{', ']': '['}
        
        for char in s:
            if char in bracket_map:
                # It's a closing bracket
                top_element = stack.pop() if stack else '#'
                
                if bracket_map[char] != top_element:
                    return False
            else:
                # It's an opening bracket
                stack.append(char)
        
        # Stack should be empty for valid parentheses
        return not stack

# Time Complexity: O(n)
# Space Complexity: O(n)''',
            'key_concepts': ['Stack', 'String', 'Hash Map']
        },
        {
            'title': 'Merge Two Sorted Lists',
            'difficulty': 'Easy',
            'problem': '''You are given the heads of two sorted linked lists list1 and list2.

Merge the two lists into one sorted list. The list should be made by splicing together the nodes of the first two lists.

Return the head of the merged linked list.

Example 1:
Input: list1 = [1,2,4], list2 = [1,3,4]
Output: [1,1,2,3,4,4]

Example 2:
Input: list1 = [], list2 = []
Output: []

Example 3:
Input: list1 = [], list2 = [0]
Output: [0]

Constraints:
- The number of nodes in both lists is in the range [0, 50].
- -100 <= Node.val <= 100
- Both list1 and list2 are sorted in non-decreasing order.
''',
            'solution': '''class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution:
    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        # Create a dummy node to simplify edge cases
        dummy = ListNode(0)
        current = dummy
        
        # Compare nodes from both lists and link the smaller one
        while list1 and list2:
            if list1.val <= list2.val:
                current.next = list1
                list1 = list1.next
            else:
                current.next = list2
                list2 = list2.next
            
            current = current.next
        
        # Link remaining nodes (if any)
        current.next = list1 or list2
        
        return dummy.next

# Time Complexity: O(m + n) where m and n are lengths of lists
# Space Complexity: O(1)''',
            'key_concepts': ['Linked List', 'Two Pointers', 'Merge']
        },
        {
            'title': 'Longest Substring Without Repeating Characters',
            'difficulty': 'Medium',
            'problem': '''Given a string s, find the length of the longest substring without repeating characters.

Example 1:
Input: s = "abcabcbb"
Output: 3
Explanation: The answer is "abc", with the length of 3.

Example 2:
Input: s = "bbbbb"
Output: 1
Explanation: The answer is "b", with the length of 1.

Example 3:
Input: s = "pwwkew"
Output: 3
Explanation: The answer is "wke", with the length of 3.

Constraints:
- 0 <= s.length <= 5 * 10^4
- s consists of English letters, digits, symbols and spaces.
''',
            'solution': '''class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        # Sliding window approach with hash map
        char_index = {}  # Maps character to its last seen index
        max_length = 0
        start = 0  # Start of current window
        
        for end in range(len(s)):
            char = s[end]
            
            if char in char_index and char_index[char] >= start:
                # Move start past the previous occurrence
                start = char_index[char] + 1
            
            # Update character's last seen index
            char_index[char] = end
            
            # Update max length
            max_length = max(max_length, end - start + 1)
        
        return max_length

# Time Complexity: O(n) where n is string length
# Space Complexity: O(min(m, n)) where m is charset size''',
            'key_concepts': ['Sliding Window', 'Hash Map', 'String']
        },
        {
            'title': 'Valid Palindrome II',
            'difficulty': 'Medium',
            'problem': '''Given a string s, return true if the s can be palindrome after deleting at most one character from it.

Example 1:
Input: s = "aba"
Output: true

Example 2:
Input: s = "abca"
Output: true
Explanation: You could delete the character 'c'.

Example 3:
Input: s = "abc"
Output: false

Constraints:
- 1 <= s.length <= 10^5
- s consists of lowercase English letters.
''',
            'solution': '''class Solution:
    def validPalindrome(self, s: str) -> bool:
        # Helper function to check if substring is palindrome
        def is_palindrome_range(i, j):
            while i < j:
                if s[i] != s[j]:
                    return False
                i += 1
                j -= 1
            return True
        
        # Two-pointer approach
        left, right = 0, len(s) - 1
        
        while left < right:
            if s[left] != s[right]:
                # Try skipping either left or right character
                skip_left = is_palindrome_range(left + 1, right)
                skip_right = is_palindrome_range(left, right - 1)
                return skip_left or skip_right
            
            left += 1
            right -= 1
        
        return True

# Time Complexity: O(n)
# Space Complexity: O(1)''',
            'key_concepts': ['Two Pointers', 'String', 'Greedy']
        }
    ]
    
    print('=' * 80)
    print('🐍 LEECODE-STYLE PYTHON INTERVIEW QUESTIONS')
    print('=' * 80)

    for i, q in enumerate(questions, 1):
        print(f'\n{i}. [{q["difficulty"]}] {q["title"]}')
        print('-' * 60)
        print(q['problem'])
        print('\n💡 Key Concepts:', ', '.join(q['key_concepts']))
        print('\n📝 Solution:')
        for line in q['solution'].split('\n'):
            if line.strip():
                print(f'    {line}')

    print('\n' + '=' * 80)
    print('💡 Tip: Try solving these on LeetCode or similar platforms!')
    print('=' * 80)

if __name__ == '__main__':
    generate_leetcode_questions()
