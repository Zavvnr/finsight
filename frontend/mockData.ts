import { Document, StockDataPoint, CompanyMetrics } from './types';

export const MOCK_DOCUMENTS: Document[] = [
  {
    id: 'doc-1',
    name: 'TechCorp_Q1_2024_Earnings.pdf',
    uploadDate: '2024-04-15',
    size: '2.4 MB',
    content: `TechCorp Q1 2024 Earnings Report.
Revenue for the first quarter was $85.2 billion, up 8% year-over-year.
Net income was $21.3 billion.
Cloud services revenue grew by 24% to $25 billion.
Hardware sales saw a slight decline of 2% due to supply chain constraints.
Guidance for Q2: We expect revenue between $87B and $89B.
Key Risks: Ongoing geopolitical tensions affecting supply chains, and increased regulatory scrutiny in European markets.
Opportunities: Expansion of our new AI-driven enterprise tools is expected to drive significant growth in the latter half of the year.`
  },
  {
    id: 'doc-2',
    name: 'TechCorp_Q2_2024_Earnings.pdf',
    uploadDate: '2024-07-20',
    size: '2.6 MB',
    content: `TechCorp Q2 2024 Earnings Report.
Revenue for the second quarter reached a record $89.5 billion, up 11% year-over-year, beating our guidance.
Net income was $23.1 billion.
Cloud services continued strong momentum, growing 28% to $28 billion.
Hardware sales rebounded, growing 5% as supply chain issues eased.
Guidance for Q3: We expect revenue between $92B and $95B.
Key Risks: Macroeconomic headwinds and potential softening of consumer spending.
Opportunities: Our recent acquisition of DataFlow Inc. will integrate seamlessly into our cloud offerings, providing new revenue streams.`
  },
  {
    id: 'doc-3',
    name: 'GlobalBank_10K_2023.pdf',
    uploadDate: '2024-02-10',
    size: '5.1 MB',
    content: `GlobalBank Annual Report (10-K) 2023.
Total net revenue for the full year was $120 billion.
Net interest income increased by 15% due to higher interest rates.
Investment banking fees declined by 10% amid a slower M&A environment.
Provision for credit losses increased to $5 billion, reflecting a more cautious economic outlook.
Strategic Focus: Accelerating digital transformation and expanding wealth management services.
Risks: Interest rate volatility, potential recessionary pressures impacting loan defaults.`
  }
];

export const MOCK_STOCK_DATA: StockDataPoint[] = Array.from({ length: 30 }).map((_, i) => {
  const date = new Date();
  date.setDate(date.getDate() - (30 - i));
  // Generate a somewhat realistic looking stock curve
  const basePrice = 150;
  const volatility = 5;
  const trend = i * 0.5;
  const randomWalk = Math.sin(i) * volatility + (Math.random() * 2 - 1) * 2;
  
  return {
    date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    price: Number((basePrice + trend + randomWalk).toFixed(2)),
    volume: Math.floor(Math.random() * 5000000) + 10000000
  };
});

export const MOCK_METRICS: CompanyMetrics = {
  symbol: 'TCRP',
  name: 'TechCorp Inc.',
  currentPrice: MOCK_STOCK_DATA[MOCK_STOCK_DATA.length - 1].price,
  change: 2.45,
  changePercent: 1.6,
  high52w: 175.20,
  low52w: 120.50,
  volume: '14.2M',
  marketCap: '$2.1T'
};
