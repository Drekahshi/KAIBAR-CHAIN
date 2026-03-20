require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.19",
  networks: {
    hedera_testnet: {
      url: "https://testnet.hashio.io/v1/jsonrpc",
      accounts: [process.env.PRIVATE_KEY || "0x0000000000000000000000000000000000000000000000000000000000000000"],
    },
  },
};
