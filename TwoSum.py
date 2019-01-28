class Solution:
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        diff = {}
        for i in range(len(nums)):
            if nums[i] in diff:
                return [diff[nums[i]], i]
            else:
                diff[target - nums[i]] = i
        return []

# Use a dictionary to record difference between each num and target
# Time: O(n)
# Space: O(n)
