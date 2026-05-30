/*
 * @lc app=leetcode id=1929 lang=cpp
 *
 * [1929] Concatenation of Array
 */

// @lc code=start
class Solution {
public:
    vector<int> getConcatenation(vector<int>& nums) {
        vector<int> ans(nums);
        ans.insert(ans.end(), nums.begin(), nums.end());
        return ans;
    }
};
// @lc code=end
