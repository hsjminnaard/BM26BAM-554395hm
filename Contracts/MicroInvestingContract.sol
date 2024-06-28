// SPDX-License-Identifier: MIT

pragma solidity ^0.6.0;

contract MicroInvestingContract {
    string public name;
    uint256 public totalSupply;
    address public owner;
    address public platformAddress = 0xc38cE885b78D11dD61cD451c2bD546b174D1a250;
    uint256 public feePercentage = 5; 

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(uint256 => uint256)) public fractionalOwnership;
    mapping(uint256 => uint256) public dividends;
    mapping(uint256 => Sale) public bondSales;

    struct Sale {
        address seller;
        uint256 price;
        bool isForSale;
    }

    event Transfer(address indexed from, address indexed to, uint256 amount);
    event BuyFraction(address indexed buyer, uint256 indexed tokenId, uint256 amount);
    event TransferFraction(address indexed from, address indexed to, uint256 indexed tokenId, uint256 amount);
    event FeePaid(address indexed payer, uint256 amount);
    event BondListedForSale(address indexed seller, uint256 indexed tokenId, uint256 price);
    event BondSold(address indexed buyer, address indexed seller, uint256 indexed tokenId, uint256 amount, uint256 price);

    constructor(string memory _name, uint256 _totalSupply) public {
        name = _name;
        totalSupply = _totalSupply;
        balanceOf[msg.sender] = _totalSupply;
        owner = msg.sender;
    }

    function buyFraction(uint256 _tokenId, uint256 _amount) external payable {
        uint256 fee = calculateFee(_amount);
        require(balanceOf[msg.sender] >= _amount + fee, "Insufficient balance to cover amount and fee");
        balanceOf[msg.sender] -= _amount + fee;
        balanceOf[platformAddress] += fee;
        fractionalOwnership[msg.sender][_tokenId] += _amount;
        emit BuyFraction(msg.sender, _tokenId, _amount);
        emit FeePaid(msg.sender, fee);
    }

    function distributeDividends(uint256 _tokenId, uint256 _dividendPerToken) external {
        require(msg.sender == owner, "Only owner can distribute dividends");
        dividends[_tokenId] += _dividendPerToken;
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

    function transferFraction(address _to, uint256 _tokenId, uint256 _amount) external {
        uint256 fee = calculateFee(_amount);
        require(fractionalOwnership[msg.sender][_tokenId] >= _amount, "Insufficient fractional ownership");
        require(balanceOf[msg.sender] >= fee, "Insufficient balance to cover fee");
        fractionalOwnership[msg.sender][_tokenId] -= _amount;
        fractionalOwnership[_to][_tokenId] += _amount;
        balanceOf[msg.sender] -= fee;
        balanceOf[platformAddress] += fee;
        emit TransferFraction(msg.sender, _to, _tokenId, _amount);
        emit FeePaid(msg.sender, fee);
    }

    function listBondForSale(uint256 _tokenId, uint256 _price) external {
        require(fractionalOwnership[msg.sender][_tokenId] > 0, "You do not own any fraction of this bond");
        bondSales[_tokenId] = Sale({
            seller: msg.sender,
            price: _price,
            isForSale: true
        });
        emit BondListedForSale(msg.sender, _tokenId, _price);
    }

    function buyBond(uint256 _tokenId) external payable {
        Sale memory sale = bondSales[_tokenId];
        require(sale.isForSale, "This bond is not for sale");
        require(msg.value == sale.price, "Incorrect value sent");

        uint256 fee = calculateFee(sale.price);
        uint256 amountToSeller = sale.price - fee;

        // Transfer the bond
        fractionalOwnership[sale.seller][_tokenId] -= 1;
        fractionalOwnership[msg.sender][_tokenId] += 1;

        // Transfer the payment
        balanceOf[platformAddress] += fee;
        balanceOf[sale.seller] += amountToSeller;

        bondSales[_tokenId].isForSale = false;

        emit BondSold(msg.sender, sale.seller, _tokenId, 1, sale.price);
        emit FeePaid(msg.sender, fee);
    }

    function calculateFee(uint256 _amount) internal view returns (uint256) {
        return (_amount * feePercentage) / 1000;
    }
}
