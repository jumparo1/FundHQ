# TAO / Bittensor — Subnet Intelligence

## What Is Bittensor
Decentralized AI marketplace — "Bitcoin for AI." Fair-launch (no pre-mine, no VC), 21M max supply, Substrate blockchain. Miners produce AI work (inference, training, data), validators evaluate quality via Yuma Consensus. 128 competing subnets, each an autonomous marketplace for a specific AI commodity.

## Tokenomics
- **Max supply:** 21,000,000 TAO (hard cap)
- **Circulating:** ~10.78M (~51%)
- **Daily emissions:** 3,600 TAO (post-1st halving Dec 14, 2025)
- **Emission split:** ~18% to subnet owner, rest to miners/validators/stakers
- **Halving schedule:** 1st complete (Dec 2025), 2nd ~late 2029, 3rd ~2033
- **Recycling:** Registration fees + tx fees removed from circulating supply, returned to unissued
- **Inflation:** ~13% annually (down from ~26% pre-halving)

## Dynamic TAO (dTAO) — Launched Feb 13, 2025
- Each subnet issues its own **alpha token** via AMM (TAO reserve + Alpha reserve)
- Alpha price = TAO_in_reserve / Alpha_in_reserve
- Must buy TAO first to access any subnet → structural buy pressure
- Emissions allocated by **net TAO flows** (staking minus unstaking) via Taoflow model
- Validator stake weight = Alpha Stake + (TAO Stake × TAO Weight Parameter)

## How Subnets Work
1. **Registration:** Pay TAO fee (recycled from supply)
2. **128-slot cap:** New subnets must outcompete lowest-performing existing ones
3. **Immunity period:** 4 months for new subnets (cannot be deregistered)
4. **Deregistration:** Lowest EMA price / net inflows get replaced
5. **Participants:** Subnet Owner (designs incentive mechanism) → Validators (evaluate quality) → Miners (perform work) → Stakers (delegate TAO)

## Subnet Directory — Tier 1 (Major / Revenue-Generating)

| NetUID | Name | Category | Description | Notes |
|--------|------|----------|-------------|-------|
| 0 | **Root** | Governance | Special subnet — no alpha token, no miners. TAO holders stake to validators subnet-agnostically | Not tradeable |
| 1 | **Apex** | Text/Agents | Improves LLM inference via agentic workflows & fine-tuning data generation | |
| 2 | **DSperse (Omron)** | Cryptography | Zero-knowledge proving network for verifiable AI model inference (zk-ML) | |
| 3 | **Templar** | Training | Decentralized collaborative LLM pre-training. Built **Covenant-72B** (72B params, March 2026) | ~30% emissions, by tplr-ai |
| 4 | **Targon** | Inference | Deterministic verification, confidential GPUs with TEE enclaves. Powers Dippy (4M+ users) | ~10% emissions, $10.4M projected rev, Manifold Labs |
| 5 | **Hone** | AGI/Research | Hierarchical AI model training toward human-level reasoning | |
| 6 | **Numinous** | Prediction | Decentralized forecasting network with LLM agents for real-world events | Infinite Games |
| 7 | **SubVortex** | Infrastructure | Decentralized subtensor node network for stability and resource allocation | |
| 8 | **Vanta (PTN)** | Trading | Decentralized prop trading — crowdsources AI-driven trading strategies/signals | |
| 9 | **IOTA** | Pre-Training | Pre-training LLMs with extensive datasets and continuous validation | |
| 10 | **Swap** | DeFi | Cross-chain DEX bridging Base/Ethereum to Bittensor subnet tokens | |
| 19 | **Nineteen** | Inference | Ultra-low-latency LLM & image inference. World record fastest LLM inference | Rayon Labs |
| 56 | **Gradients** | Training | Simplifies AI training via decentralized network, no technical skills needed | Rayon Labs |
| 64 | **Chutes** | Inference/Compute | Serverless AI compute, open-source models at lowest market price. 8,000+ GPUs, 160B tokens/day, 90% cheaper than AWS, 400K+ users | Rayon Labs |

**Rayon Labs** runs SN19 + SN56 + SN64 = 23%+ of total emissions. Major concentration risk.

## Subnet Directory — Tier 2 (Active & Notable)

| NetUID | Name | Category | Description |
|--------|------|----------|-------------|
| 12 | **ComputeHorde** | GPU Compute | Decentralized GPU compute network for validation tasks |
| 13 | **Data Universe** | Data | Collects, aggregates, stores large-scale data for AI training |
| 14 | **TAO Hash** | Mining | Bitcoin miners redirect hash rate for alpha token rewards |
| 15 | **BitQuant** | Finance | Real-time crypto/DeFi market analysis using quantitative agents |
| 16 | **BitAds** | Advertising | Decentralized pay-per-sale advertising — brands pay only for verified conversions |
| 17 | **Gen 404** | 3D/Gaming | Creates 3D worlds and games through AI text/image descriptions |
| 18 | **Zeus** | Weather | Environmental/weather forecasting using incentivized model innovation |
| 20 | **Bounty Hunter** | Benchmarks | Open bounty competitions rewarding winning AI models on benchmarks |
| 21 | **Any-to-Any** | Multimodal | Decentralized multimodal AI (text, voice, image orchestration) |
| 22 | **Desearch** | Search | AI-powered decentralized search engine. Social/search data analysis |
| 23 | **Trishool** | Safety | Adversarially tests AI models and autonomously aligns them |
| 24 | **Quasar** | Text/Context | Language models with near-infinite memory for long-context tasks |
| 25 | **Mainframe** | Biotech | Decentralized protein folding research for drug discovery |
| 26 | **Kinitro** | Robotics | Accelerates robotic intelligence through incentivized competitions |
| 27 | **Nodexo** | GPU Cloud | Decentralized GPU cloud marketplace |
| 30 | **Wahoot** | Prediction | Real-time prediction market covering global events, rewards in TAO |
| 32 | **It's AI** | Detection | Detects AI-generated content and verifies text authenticity |
| 34 | **BitmMind** | Deepfake Detection | Detects AI-generated images using decentralized detection models |
| 35 | **Cartha** | DeFi | Decentralized liquidity engine for multi-asset DEX trading |
| 37 | **Aurelius** | Safety | Finds LLM misalignment errors, produces verifiable safety datasets |
| 40 | **Chunking** | RAG | Advances retrieval-augmented generation through smart data chunking |
| 41 | **Almanac** | Sports/Trading | Market intelligence for sports predictions and trading signals |
| 43 | **Graphite** | Graph Problems | Specialized in graphical/combinatorial optimization problems |
| 44 | **Score** | Sports | Reliable sports statistics and football match prediction rewards |
| 46 | **RESI** | Real Estate | Building world's largest open real estate database |
| 48 | **Quantum Compute** | Quantum | Marketplace for decentralized quantum computing capacity |
| 50 | **Synth** | Finance | Probabilistic price forecasts for BTC with synthetic data generation |
| 51 | **Lium** | GPU Rental | Decentralized GPU rental platform |
| 52 | **Dojo** | Training Data | Community-driven multi-modal AI training data generation & curation |
| 53 | **Efficient Frontier** | Trading | Optimizes crypto trading strategies using decentralized ML |
| 57 | **Sportstensor** | Sports | Decentralized sports prediction with crowdsourced data on Polymarket |
| 58 | **Handshake** | Payments | Trustless USDC payment channels for AI agents |
| 59 | **BabelBit** | Translation | Real-time speech-to-speech translation using predictive LLMs |
| 60 | **Bitsec** | Security | AI-driven detection and fixing of code/smart contract vulnerabilities |
| 61 | **RedTeam** | Cybersecurity | Competitive cybersecurity challenges, anti-bot, anti-fraud |
| 62 | **Ridges AI** | Coding Agents | Decentralized marketplace for autonomous software development agents |
| 65 | **TAO Private Network** | VPN | Decentralized, anonymous VPN with censorship resistance |
| 68 | **NOVA (MetaNova)** | Drug Discovery | Accelerates and democratizes drug discovery via crowdsourced models |
| 75 | **Hippius** | Storage | Blockchain-backed cloud storage for AI datasets and models |
| 76 | **Safe Scan** | Healthcare | AI cancer screening via free, open-source smartphone detection tools |
| 77 | **Liquidity** | DeFi | Incentivizes liquidity provisioning for Bittensor ecosystem tokens |
| 84 | **ChipForge** | Hardware | Open-source collaborative AI-driven integrated circuit design |
| 85 | **Vidaio** | Video | AI-powered video upscaling and compression |
| 89 | **InfiniteHash** | Mining | Decentralized Bitcoin mining pool with Lightning Network integration |
| 120 | **Affine** | RL | Incentivized reinforcement learning platform |

## Subnet Directory — Tier 3 (Smaller / Newer / Niche)

| NetUID | Name | Category | Description |
|--------|------|----------|-------------|
| 29 | AI-ASSeSS | Training | Collaborative model training with knowledge exchange |
| 33 | ReadyAI | Dialogue | Builds extensive dialogue datasets collaboratively |
| 36 | Web Agents | Automation | AI-driven web automation agents for dynamic websites |
| 39 | Basilica | Compute | Trustless GPU compute marketplace with verification |
| 42 | Gopher | Data | Scrapes and structures real-time data into AI-ready datasets |
| 45 | Talisman AI | Crypto Signals | Mines live crypto signals (social, on-chain, market data) |
| 54 | MIID | Compliance | Generates synthetic identities for financial compliance testing |
| 63 | Quantum Innovate | Quantum Sim | Simulates quantum circuits on classical hardware |
| 66 | AlphaCore | DevOps | Autonomous DevOps agent network for infrastructure management |
| 67 | Tenex | Trading | Decentralized long-only margin trading for subnet tokens |
| 70 | Vericore | Fact-Check | Large-scale fact-checking with semantic verification |
| 71 | Leadpoet | Sales | Autonomous AI agents for finding and qualifying sales leads |
| 72 | StreetVision | Autonomous Driving | Crowdsourced street imagery for self-driving cars |
| 73 | Metahash | Token Swap | Decentralized subnet swapping ALPHA for META tokens |
| 74 | Gittensor | Open Source | Rewards open-source developers for code contributions |
| 78 | Loosh | Consciousness | Machine consciousness research for robotics and agents |
| 79 | taos | Sim Trading | Simulates decentralized financial markets for AI trading |
| 80 | Dogelayer | Mining | Merges Dogecoin/Litecoin mining with AI validation |
| 81 | Grail | Training | Permissionless distributed training on global GPU network |
| 82 | Hermes | Blockchain Data | Optimizes GraphQL AI agents for blockchain data queries |
| 83 | CliqueAI | Math | Maximum clique solver network for NP-hard problems |
| 88 | Investing | Staking | Optimizes staking strategies via transparent scoring |
| 91 | Tensorprox | Security | DDoS mitigation and cybersecurity-as-a-service |
| 93 | Bitcast | Creator | Connects YouTube creators with brands directly |
| 94 | Bitsota | Search | Distributed compute functioning as search engine for AI models |
| 96 | FLOCK OFF | Edge AI | Crowdsources compact datasets for edge AI model training |
| 97 | FlameWire | RPC | Decentralized multi-chain RPC gateway |
| 98 | Forever Money | DeFi | AI-driven liquidity manager optimizing DEX pools |
| 100 | Platform | Research | Collaborative AI research via multiple challenge environments |
| 103 | Djinn | Sports | Encrypted sports signals marketplace with attestations |
| 106 | Liquidity Provisioning | DeFi | Coordinates Bittensor liquidity via Solana using wTAO tokens |
| 111 | oneoneone | Data | Collects and validates user-generated web content for AI |
| 112 | minotaur | DeFi | AI-driven DEX aggregator and swap-routing engine |
| 116 | TaoLend | Lending | TAO lending protocol against ALPHA collateral |
| 117 | BrainPlay | Gaming | AI models competing in games to benchmark reasoning |
| 118 | HODL ETF | Index | Rewards long-term TAO stakers through index incentives |
| 121 | sundae_bar | Marketplace | Connects agent developers with users |
| 122 | Bitrecs | Recommendations | Decentralized recommendation engine for e-commerce |
| 123 | MANTIS | Forecasting | AI-driven forecasting rewarding high-quality predictions |
| 124 | Swarm | Drones | Decentralized autopilot network for autonomous drones |
| 128 | ByteLeap | Cloud | Blockchain-enhanced cloud platform for AI training/inference |

## Subnet Categories Summary

| Category | Count | Top Subnets |
|----------|-------|-------------|
| AI Inference | 5+ | Chutes (64), Targon (4), Nineteen (19), Apex (1) |
| AI Training | 5+ | Templar (3), IOTA (9), Gradients (56), Grail (81) |
| Finance/Trading | 8+ | Vanta (8), Efficient Frontier (53), Synth (50), BitQuant (15) |
| DeFi | 6+ | Swap (10), Cartha (35), Liquidity (77), TaoLend (116) |
| Data | 4+ | Data Universe (13), Dojo (52), Gopher (42) |
| Prediction | 5+ | Numinous (6), Wahoot (30), Sportstensor (57), MANTIS (123) |
| GPU Compute | 4+ | ComputeHorde (12), Lium (51), Nodexo (27) |
| Security | 3+ | Bitsec (60), RedTeam (61), Tensorprox (91) |
| Biotech/Health | 3+ | Mainframe (25), NOVA (68), Safe Scan (76) |
| Mining (BTC/DOGE) | 3 | TAO Hash (14), InfiniteHash (89), Dogelayer (80) |
| Robotics/HW | 3 | Kinitro (26), ChipForge (84), Swarm (124) |

## Scam Warnings
Per taosubnetguide.com, several subnets flagged "Scam until proven otherwise": AI Factory, Inactive, Internet, Rich Kids, Signal, Tigeralpha, and multiple "Unclaimed" / "Unknown" entries. Always verify subnet teams and products before investing in alpha tokens.

## Key Catalysts (as of March 2026)
1. **Grayscale ETF** — S-1 filed Dec 30, 2025; SEC-reporting status March 14, 2026; first U.S. TAO ETF filed March 15
2. **Covenant-72B** — 72B param LLM pre-trained entirely on decentralized Bittensor (SN3 Templar), March 10, 2026
3. **Post-halving squeeze** — Daily emissions halved (7,200 → 3,600), dTAO drives demand
4. **Upbit listing** — Korea's #1 exchange, late February 2026
5. **Nvidia Rubin chips** — Reduces inference costs, benefits compute-heavy subnets

## Investment Thesis

### Bull Case
- Fair-launch Bitcoin model for AI — no VC unlock risk, 21M cap, deflationary
- dTAO creates structural TAO demand (must buy TAO to access any subnet)
- Real revenue — Targon $10.4M/yr projected, Chutes 90% cheaper than AWS with 400K+ users
- Grayscale ETF opens institutional access
- Darwinian 128-subnet competition ensures quality
- Covenant-72B proved decentralized training can produce frontier-scale models

### Bear Case
- Subnet quality varies wildly — many unknown/flagged subnets
- Rayon Labs concentration — 3 subnets control 23%+ of emissions
- No moat on individual subnets — any can be outcompeted and deregistered
- Complexity barrier — dTAO + alpha tokens + 128 subnets = steep learning curve
- Competition from Render, Akash, io.net in decentralized compute
- Regulatory uncertainty at AI + crypto intersection

## Tracking Resources
| Resource | URL | Use |
|----------|-----|-----|
| Taostats | taostats.io/subnets | Emissions, ownership, registration dates |
| TaoMarketCap | taomarketcap.com | All subnets, validators, prices, portfolio |
| Subnet Alpha | subnetalpha.ai | Subnet descriptions, teams, roadmaps |
| Tao Subnet Guide | taosubnetguide.com | All 128 subnets with scam warnings |
| SubnetStats | subnetstats.app | Subnet analytics |
| Bittensor Docs | docs.learnbittensor.org | Official documentation |
| Bittensor Halving | bittensorhalving.com | Halving countdown + supply calculator |
| CoinGecko Category | coingecko.com/en/categories/bittensor-subnets | Subnet token market caps |
