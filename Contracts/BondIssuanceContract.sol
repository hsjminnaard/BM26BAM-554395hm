// SPDX-License-Identifier: MIT

pragma solidity ^0.6.0;

contract BondIssuanceContract {
    struct Bond {
        uint256 id;
        string name;
        uint256 totalSupply;
        uint256 remainingSupply;
        uint256 price;
        address issuer;
        bool thirdPartyVerified;
        mapping(address => uint256) balanceOf;
    }

    uint256 public nextBondId;
    mapping(uint256 => Bond) public bonds;
    mapping(address => bool) public verifiedUsers;
    address public thirdPartyVerifier;

    event BondIssued(uint256 indexed id, string name, uint256 totalSupply, uint256 price, address indexed issuer);
    event BondPurchased(uint256 indexed id, address indexed buyer, uint256 amount);
    event BondVerified(uint256 indexed id, bool status);

    modifier onlyThirdPartyVerifier() {
        require(msg.sender == thirdPartyVerifier, "Only third-party verifier can perform this action");
        _;
    }

    modifier onlyVerifiedUsers() {
        require(verifiedUsers[msg.sender], "User not verified");
        _;
    }

    constructor(address _thirdPartyVerifier) public {
        nextBondId = 1;
        thirdPartyVerifier = _thirdPartyVerifier;
    }

    function verifyUser(address _user, bool _status) public onlyThirdPartyVerifier {
        verifiedUsers[_user] = _status;
    }

    function issueBond(string memory _name, uint256 _totalSupply, uint256 _price) public onlyVerifiedUsers {
        bonds[nextBondId] = Bond({
            id: nextBondId,
            name: _name,
            totalSupply: _totalSupply,
            remainingSupply: _totalSupply,
            price: _price,
            issuer: msg.sender,
            thirdPartyVerified: false
        });
        emit BondIssued(nextBondId, _name, _totalSupply, _price, msg.sender);
        nextBondId++;
    }

    function verifyBond(uint256 _bondId, bool _status) public onlyThirdPartyVerifier {
        Bond storage bond = bonds[_bondId];
        require(bond.id != 0, "Bond does not exist");
        bond.thirdPartyVerified = _status;
        emit BondVerified(_bondId, _status);
    }

    function purchaseBond(uint256 _bondId, uint256 _amount) public payable onlyVerifiedUsers {
        Bond storage bond = bonds[_bondId];
        require(bond.id != 0, "Bond does not exist");
        require(bond.thirdPartyVerified, "Bond not verified by third party");
        require(bond.remainingSupply >= _amount, "Not enough bonds available");
        require(msg.value == _amount * bond.price, "Incorrect Ether value");

        bond.balanceOf[msg.sender] += _amount;
        bond.remainingSupply -= _amount;

        emit BondPurchased(_bondId, msg.sender, _amount);
    }

    function withdraw() public {
        payable(msg.sender).transfer(address(this).balance);
    }
}
