// SPDX-License-Identifier: MIT

pragma solidity ^0.6.0;

contract SubscriptionContract {
    uint256 public subscriptionFee = 10 ether; 

    mapping(address => bool) public isSubscriber;
    mapping(address => uint256) public nextSubscriptionDue;

    event SubscriptionRenewed(address indexed user, uint256 nextDueTimestamp);

    constructor() public {
        isSubscriber[msg.sender] = true;
        nextSubscriptionDue[msg.sender] = now + 30 days;
    }

    function renewSubscription() external payable {
        require(msg.value >= subscriptionFee, "Insufficient subscription fee provided");

        if (!isSubscriber[msg.sender]) {
            isSubscriber[msg.sender] = true;
        }

        nextSubscriptionDue[msg.sender] = now + 30 days; 
        emit SubscriptionRenewed(msg.sender, nextSubscriptionDue[msg.sender]);
    }

    function isSubscriptionDue(address user) external view returns (bool) {
        return now >= nextSubscriptionDue[user];
    }

    function paySubscriptionFee() external payable {
        require(isSubscriber[msg.sender], "User is not a subscriber");
        require(msg.value >= subscriptionFee, "Insufficient subscription fee provided");
    }
}
