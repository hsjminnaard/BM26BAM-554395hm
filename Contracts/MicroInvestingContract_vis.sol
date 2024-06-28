// SPDX-License-Identifier: MIT

pragma solidity ^0.6.0;

contract MicroInvestingContract {
    string public name;
    uint256 public totalSupply;
    address public owner;
    address public platformAddress = 0xc38cE885b78D11dD61cD451c2bD546b174D1a250;
    uint256 public feePercentage = 5; 

    mapping(address => uint256) public balanceOf;

    event Transfer(address indexed from, address indexed to, uint256 amount);
    event FeePaid(address indexed payer, uint256 amount);

    constructor(string memory _name, uint256 _totalSupply) public {
        name = _name;
        totalSupply = _totalSupply;
        balanceOf[msg.sender] = _totalSupply;
        owner = msg.sender;
    }

    function transfer(address _to, uint256 _amount) external {
        uint256 fee = calculateFee(_amount);
        require(balanceOf[msg.sender] >= _amount + fee, "Insufficient balance to cover amount and fee");
        balanceOf[msg.sender] -= _amount + fee;
        balanceOf[_to] += _amount;
        balanceOf[platformAddress] += fee;
        emit Transfer(msg.sender, _to, _amount);
        emit FeePaid(msg.sender, fee);
    }

    function calculateFee(uint256 _amount) internal view returns (uint256) {
        return (_amount * feePercentage) / 1000;
    }
}
