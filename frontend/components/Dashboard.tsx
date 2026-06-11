import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Activity, BarChart2 } from 'lucide-react';
import { MOCK_STOCK_DATA, MOCK_METRICS } from '../mockData';

const Dashboard: React.FC = () => {
  const isPositive = MOCK_METRICS.change >= 0;

  return (
    <div className="p-6 h-full overflow-y-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900">Market Overview</h1>
        <p className="text-slate-500">Real-time insights and historical data</p>
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-500">{MOCK_METRICS.symbol}</p>
              <h3 className="text-2xl font-bold text-slate-900">${MOCK_METRICS.currentPrice.toFixed(2)}</h3>
            </div>
            <div className={`p-2 rounded-lg ${isPositive ? 'bg-emerald-100 text-emerald-600' : 'bg-rose-100 text-rose-600'}`}>
              {isPositive ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
            </div>
          </div>
          <div className="mt-4 flex items-center text-sm">
            <span className={`font-medium ${isPositive ? 'text-emerald-600' : 'text-rose-600'}`}>
              {isPositive ? '+' : ''}{MOCK_METRICS.change} ({MOCK_METRICS.changePercent}%)
            </span>
            <span className="text-slate-400 ml-2">Today</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-500">Market Cap</p>
              <h3 className="text-2xl font-bold text-slate-900">{MOCK_METRICS.marketCap}</h3>
            </div>
            <div className="p-2 rounded-lg bg-blue-100 text-blue-600">
              <DollarSign size={20} />
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-500">Volume</p>
              <h3 className="text-2xl font-bold text-slate-900">{MOCK_METRICS.volume}</h3>
            </div>
            <div className="p-2 rounded-lg bg-indigo-100 text-indigo-600">
              <Activity size={20} />
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm font-medium text-slate-500">52W Range</p>
              <h3 className="text-lg font-bold text-slate-900 mt-1">
                ${MOCK_METRICS.low52w} - ${MOCK_METRICS.high52w}
              </h3>
            </div>
            <div className="p-2 rounded-lg bg-purple-100 text-purple-600">
              <BarChart2 size={20} />
            </div>
          </div>
          <div className="mt-3 w-full bg-slate-100 rounded-full h-1.5">
            <div 
              className="bg-indigo-500 h-1.5 rounded-full" 
              style={{ width: `${((MOCK_METRICS.currentPrice - MOCK_METRICS.low52w) / (MOCK_METRICS.high52w - MOCK_METRICS.low52w)) * 100}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Chart Section */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm mb-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-lg font-bold text-slate-900">Price History (30 Days)</h2>
          <div className="flex space-x-2">
            {['1D', '1W', '1M', '3M', '1Y'].map(period => (
              <button 
                key={period} 
                className={`px-3 py-1 text-sm rounded-md ${period === '1M' ? 'bg-indigo-50 text-indigo-600 font-medium' : 'text-slate-500 hover:bg-slate-50'}`}
              >
                {period}
              </button>
            ))}
          </div>
        </div>
        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={MOCK_STOCK_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dy={10} />
              <YAxis domain={['auto', 'auto']} axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
              <Tooltip 
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                itemStyle={{ color: '#0f172a', fontWeight: 500 }}
              />
              <Area type="monotone" dataKey="price" stroke="#6366f1" strokeWidth={2} fillOpacity={1} fill="url(#colorPrice)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
