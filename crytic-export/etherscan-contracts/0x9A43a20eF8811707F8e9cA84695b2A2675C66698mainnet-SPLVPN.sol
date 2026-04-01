// SPDX-License-Identifier: MIT

// SPL VPN
// https://linktr.ee/splvpn
// https://www.splvpn.ai
// https://x.com/SplVpn
// https://t.me/officialsplvpn
// https://www.facebook.com/splvpn/
// https://www.instagram.com/spl_vpn/
// https://www.pinterest.com/splvpn/
// https://www.youtube.com/@splvpn/
// https://github.com/spl-secure-vpn
// https://opensea.io/collection/spl-vpn

/**

                                                                                                                                                                                                                                                                                                                                                                                                 
                                                                                                    
         O(|||(|||||||||||||||||||||||||||||||||\\\\|||||||||||||||||||||||||||||||||||||||         
         z|((|(||||||||(((((((((((((((((((((((((((((((((((((((((((((((((((((((((||((((((|||$        
         Q((((((((|((|((((|(((((((((((((|||((|((((((((((((((((((((((((((((|||(((|(((((((|||$        
         J(((((((((((||(((((((((((((||||(|||(((((((((((((((|((((((|(((||((|||||(((|(((((((|$        
         0(((((((((((|(|(((((((((|||||||||(((|((((((((|((((((|((((((((((((||(((|||||||((||($        
         z((((((((((((((|(((((|(|((||||||(((|((|||(((|((((|((((((((((((||||((((||||((((|||($        
         Y((((((((|1                                        Y(((((((((((|||||||||||((((||(($        
         Q(((((((((1                                           |)(||||((||||||||||||||((|(($        
         O(((((((((1                                               1((||||(|||||||||||(||(($        
         Q((((((((((                                                 1|(((||||||(((((|||||($        
         z(((((((((((||                  uxnnnnnnnnnnnnnn              <)|(||(((((||||||||($        
         z(((((|||||(|||($              Qunnuunnnnuuunnnunun              {||(|(|||||(||||($        
         r)((||||(||||||||(|             xunnnnnuunnnnnnuuuunu              {)(||||||||||||$        
          1)((|||((|||||(||||)$             runnnnnnnnnnnuuuuuuuv              {f(((|||||||$        
             )||((((((||||||||(((r              nnnnnnnnnnnuuuuuunun              r\((|||||$        
               )((((((((|(|||||||(((r             xnnnnnnnnnnuuuuuuuuuu              ||||||$        
                  )|)(((((((|||||||||(n             1xnnnnnnnnnnnunnunuvnd             \(((         
                    )|((((((((((((|||||(|r             nvxnnnnnnnnnnnuuuuuun                        
                       {\)((((((((((((|||()c             1nnunnnnnnnnnnnuunuuxd                     
          xxuv            Y(((((((((((||||||||t              cxnnnnnnnnnnnuuuuuxuL                  
         Uuuuunvu            \(((((((||(((|||||(|{             unnnnnnnnnnnnnnuuuuxxz               
         Unnnnnnnnx            z)(((((((((||||(||||)              cnnnnnnnnnnnnnuuuunnv             
         Qnnnnnnuunuun            ()(((((((((((||||(||)             Junxnnnnnnnnnnuunnnxnn          
         Qnnnnnnnnnnuunx            x(1((((((((((((|||||(              Yxnxnnnnnnnnnnnnnnnx         
         Qnnnnnnnnnnunnunxj             {|((||((((((||||||||               xxnnunnnnnnnnnnn$        
         Qnnnnnnnnnnnnnnnnnnxu$            )(((((||((((||||||)|Q             unnnnnnnnnnnnn$        
         LnnnnnnnnnnnnnnnnnnuuunX            {)|((((((((||((|||||\              xnnnnnnnnnn$        
         Cnnnnnnnnnnnnnnnnnnuuuuunuo            ((((((((((||||||||(|z            xnnnnnnnnn$        
         CnnnnnnnnnnnnnnnnnunnnuuuuuuY            1|||((((||||||||||||t          nnnnnnnnnn$        
         Qnnnnnnnnnnnnnnnnnnnnnuuuuuuunuw            /((|||||||||||||||(|z       nnnnnnnnnn$        
         Cnnnnnnnnux   xnnnnunnuuuuuuuuuuucx            t\(((||||((||||||||/     nnnnnnnnnu$        
         Znnnnnnnunx     rxnnnnnnnnnuuuuuunuuun           ||((((((||(|||((n      nnnnnnnnuu$        
         Cnnnnnnnunx        xnnnnnnnuuuuunnuuuuun            /((|||||((f         nnnnnnnnun$        
         Znnnnnnnuun          jnnnnnnnnnnnnnnnuuuunn           ||)|(|r          vnnnnnnunnn$        
         Lnnnnnnnuuuuuv          rnnnnnnnnnnnnnnuuuuun                       vunnnnnnnnnnuna        
         0nnnnnnnnuuununvu          Yunnnnnnnnnnnuuuuunnn                 YXxunnnnnnnnnnnnna        
         XnnnnnnnnnnuuuuuuvvX         Onnnnnnnnnnnuuunnnnnn             vnnnunnnnnnnnnnnnnn$        
          xxnnnnnnnnnuuuuuuuuvu          uxnnnnnnnnnnnuuunx          Jununnnnnnnnnnnnnunnx          
             nxxnnnnnnnnnuuuunnux          1nnnnunuunnxnx          cnnnnnnnnnnnnnnnnnun             
               nxnnnnnnnnnnnnnnuunun          nuxnnnuu          Jununnnnnnnnnnnnnuunv               
                  1nxnnnnnnnnnnuunnnnn           11           uxnnnnnnnnnnnnnnnnnz                  
                     cnnnnnnnnnnnnnuuununu                zununnnnnnnnnnnnnnnnn                     
                        nxnnnnnnnnnnnnunununz           Xnnnnnnnnnnnnnnnnnnx                        
                          cnxnnnnnnnnnnuuuuuunu      xunnnnnnnnnnnnnnnnuux                          
                             xxnnnnnnnnnnnnnnnnunw $nnnnnnnnnnnnnnnnnnnO                            
                               xrxnnnnnnnnnnnnnnuunnnnnnnnnnnnnnnnnux                               
                                   xnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn                                  
                                      xnnunnnnnnnnnnnnnnnnnnnux                                     
                                        xnnnnnnnnnnnnnnnnnnuu                                       
                                           xnnnnnnnuunuuunO                                         
                                             xnxnnnnnuux                                            
                                                xnnn                                                
                                                                                                    
                                                                                                    


**/

pragma solidity ^0.8.0;

abstract contract Context {
    function _msgSender() internal view virtual returns (address) {
        return msg.sender;
    }

    function _msgData() internal view virtual returns (bytes calldata) {
        return msg.data;
    }
}

pragma solidity ^0.8.0;

interface IERC20 {

    event Transfer(address indexed from, address indexed to, uint256 value);

    event Approval(address indexed owner, address indexed spender, uint256 value);

    function totalSupply() external view returns (uint256);

    function balanceOf(address account) external view returns (uint256);

    function transfer(address to, uint256 amount) external returns (bool);

    function allowance(address owner, address spender) external view returns (uint256);

    function approve(address spender, uint256 amount) external returns (bool);

    function transferFrom(
        address from,
        address to,
        uint256 amount
    ) external returns (bool);
}


pragma solidity ^0.8.0;

interface IERC20Metadata is IERC20 {
    
    function name() external view returns (string memory);

    function symbol() external view returns (string memory);

    function decimals() external view returns (uint8);
}


contract Ownable is Context {
    address private _owner;
 
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
 
    constructor () {
        address msgSender = _msgSender();
        _owner = msgSender;
        emit OwnershipTransferred(address(0), msgSender);
    }
 
    function owner() public view returns (address) {
        return _owner;
    }

    modifier onlyOwner() {
        require(_owner == _msgSender(), "Ownable: caller is not the owner");
        _;
    }
 
    function renounceOwnership() public virtual onlyOwner {
        emit OwnershipTransferred(_owner, address(0));
        _owner = address(0);
    }
 
    function transferOwnership(address newOwner) public virtual onlyOwner {
        require(newOwner != address(0), "Ownable: new owner is the zero address");
        emit OwnershipTransferred(_owner, newOwner);
        _owner = newOwner;
    }
    }

pragma solidity ^0.8.0;

contract SPLVPN is Context, IERC20, IERC20Metadata, Ownable {
    mapping(address => uint256) private _balances;

    mapping(address => mapping(address => uint256)) private _allowances;

    uint256 private _totalSupply;

    string private _name;
    string private _symbol;

    constructor (string memory name_, string memory symbol_, uint256 totalSupply_) {
        _name = name_;
        _symbol = symbol_;
        _totalSupply = totalSupply_;
        _balances[msg.sender] = totalSupply_;
        emit Transfer(address(0), msg.sender, totalSupply_); 
    }

    function name() public view virtual override returns (string memory) {
        return _name;
    }

    function symbol() public view virtual override returns (string memory) {
        return _symbol;
    }

    function decimals() public view virtual override returns (uint8) {
        return 18;
    }

    function totalSupply() public view virtual override returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address account) public view virtual override returns (uint256) {
        return _balances[account];
    }

    function transfer(address to, uint256 amount) public virtual override returns (bool) {
        address owner = _msgSender();
        _transfer(owner, to, amount);
        return true;
    }

    function allowance(address owner, address spender) public view virtual override returns (uint256) {
        return _allowances[owner][spender];
    }

    function approve(address spender, uint256 amount) public virtual override returns (bool) {
        address owner = _msgSender();
        _approve(owner, spender, amount);
        return true;
    }

    function transferFrom(
        address from,
        address to,
        uint256 amount
    ) public virtual override returns (bool) {
        address spender = _msgSender();
        _spendAllowance(from, spender, amount);
        _transfer(from, to, amount);
        return true;
    }

    function increaseAllowance(address spender, uint256 addedValue) public virtual returns (bool) {
        address owner = _msgSender();
        _approve(owner, spender, allowance(owner, spender) + addedValue);
        return true;
    }

    function decreaseAllowance(address spender, uint256 subtractedValue) public virtual returns (bool) {
        address owner = _msgSender();
        uint256 currentAllowance = allowance(owner, spender);
        require(currentAllowance >= subtractedValue, "ERC20: decreased allowance below zero");
        unchecked {
            _approve(owner, spender, currentAllowance - subtractedValue);
        }

        return true;
    }

    function _transfer(
        address from,
        address to,
        uint256 amount
    ) internal virtual {
        require(from != address(0), "ERC20: transfer from the zero address");
        require(to != address(0), "ERC20: transfer to the zero address");

        _beforeTokenTransfer(from, to, amount);

        uint256 fromBalance = _balances[from];
        require(fromBalance >= amount, "ERC20: transfer amount exceeds balance");
        unchecked {
            _balances[from] = fromBalance - amount;
        }
        _balances[to] += amount;

        emit Transfer(from, to, amount);

        _afterTokenTransfer(from, to, amount);
    }

    function _approve(
        address owner,
        address spender,
        uint256 amount
    ) internal virtual {
        require(owner != address(0), "ERC20: approve from the zero address");
        require(spender != address(0), "ERC20: approve to the zero address");

        _allowances[owner][spender] = amount;
        emit Approval(owner, spender, amount);
    }

    function _spendAllowance(
        address owner,
        address spender,
        uint256 amount
    ) internal virtual {
        uint256 currentAllowance = allowance(owner, spender);
        if (currentAllowance != type(uint256).max) {
            require(currentAllowance >= amount, "ERC20: insufficient allowance");
            unchecked {
                _approve(owner, spender, currentAllowance - amount);
            }
        }
    }

    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal virtual {}

    function _afterTokenTransfer(
        address from,
        address to,
        uint256 amount
    ) internal virtual {}
}