/**
 * @title deploy.js
 * @dev Script to deploy the KaibarVault contract to the Hedera Testnet using the Hashio RPC Relay.
 * Make sure to configure your .env file with PRIVATE_KEY.
 */
const hre = require("hardhat");

async function main() {
  console.log("Starting deployment of KaibarVault...");

  const Vault = await hre.ethers.getContractFactory("KaibarVault");
  const vault = await Vault.deploy();

  await vault.deployed();

  console.log("KaibarVault successfully deployed!");
  console.log("Contract Address:", vault.address);
  console.log("Network: Hedera Testnet (via Hashio)");
  
  // NOTE: Save this address to your kai_bot/.env file as VAULT_CONTRACT_ID
}

main().catch((error) => {
  console.error("Deployment failed:", error);
  process.exitCode = 1;
});
