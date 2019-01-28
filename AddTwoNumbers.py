# Definition for singly-linked list.
# class ListNode:
#     def __init__(self, x):
#         self.val = x
#         self.next = None

class Solution:
    def addTwoNumbers(self, l1, l2):
        """
        :type l1: ListNode
        :type l2: ListNode
        :rtype: ListNode
        """
        if not l1: return l2
        if not l2: return l1

        head = ListNode(0)
        res = head
        p1 = l1
        p2 = l2
        carry = 0
        while p1 or p2:
            val = (p1.val if p1 else 0) + (p2.val if p2 else 0) + carry
            if val >= 10:
                val -= 10
                carry = 1
            else:
                carry = 0
            res.next = ListNode(val)
            res = res.next
            p1 = p1.next if p1 else p1
            p2 = p2.next if p2 else p2

        if carry != 0:
            res.next = ListNode(carry)
        return head.next

# 易错点：退出while loop以后检查carry
# l1 has n nodes, l2 has m nodes
# Time: O(max(n, m))
# Space: O(max(n, m))
