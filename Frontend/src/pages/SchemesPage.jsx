import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Mic, IndianRupee, Bookmark, BookmarkCheck, LayoutGrid } from 'lucide-react'
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'

const DISCOVERABLE_SCHEMES = [
  {
    id: 'pm-kisan',
    title: 'PM Kisan Samman Nidhi',
    category: 'Agriculture',
    payout: '₹6,000 / year',
    status: 'Eligible',
    gradient: 'from-teal-500 to-emerald-600',
    description: 'Financial assistance of ₹6,000 per year to small and marginal farmers in three installments of ₹2,000 each.',
    ministry: 'Ministry of Agriculture',
  },
  {
    id: 'pmay-urban',
    title: 'PM Awas Yojana (Urban)',
    category: 'Housing',
    payout: '₹2.67 L subsidy',
    status: 'Check Eligibility',
    gradient: 'from-indigo-500 to-blue-600',
    description: 'Credit-linked subsidy for construction or purchase of houses for economically weaker sections and low income groups.',
    ministry: 'Ministry of Housing',
  },
  {
    id: 'pmay-gramin',
    title: 'PM Awas Yojana (Gramin)',
    category: 'Housing',
    payout: '₹1.2 L – ₹1.3 L',
    status: 'Check Eligibility',
    gradient: 'from-violet-500 to-purple-600',
    description: 'Assistance to rural BPL households for construction of pucca houses with basic amenities.',
    ministry: 'Ministry of Rural Development',
  },
  {
    id: 'ayushman-bharat',
    title: 'Ayushman Bharat – PM-JAY',
    category: 'Health',
    payout: '₹5 L / year',
    status: 'Eligible',
    gradient: 'from-rose-500 to-red-600',
    description: 'World largest health insurance scheme providing ₹5 lakh per family per year for secondary and tertiary hospitalisation.',
    ministry: 'Ministry of Health',
  },
  {
    id: 'pmjdy',
    title: 'PM Jan Dhan Yojana',
    category: 'Financial Inclusion',
    payout: 'Zero Balance A/C',
    status: 'Eligible',
    gradient: 'from-amber-500 to-orange-600',
    description: 'Universal access to banking facilities with overdraft facility of ₹10,000 and accidental insurance cover of ₹2 lakh.',
    ministry: 'Ministry of Finance',
  },
  {
    id: 'pmsby',
    title: 'PM Suraksha Bima Yojana',
    category: 'Insurance',
    payout: '₹2 L cover @ ₹20/yr',
    status: 'Eligible',
    gradient: 'from-cyan-500 to-teal-600',
    description: 'Accidental death and disability insurance cover of ₹2 lakh at a premium of just ₹20 per year.',
    ministry: 'Ministry of Finance',
  },
  {
    id: 'pmjjby',
    title: 'PM Jeevan Jyoti Bima Yojana',
    category: 'Insurance',
    payout: '₹2 L @ ₹436/yr',
    status: 'Eligible',
    gradient: 'from-sky-500 to-blue-600',
    description: 'Life insurance cover of ₹2 lakh for death due to any cause at an annual premium of ₹436.',
    ministry: 'Ministry of Finance',
  },
  {
    id: 'mudra',
    title: 'PM MUDRA Yojana',
    category: 'Entrepreneurship',
    payout: 'Up to ₹10 L loan',
    status: 'Check Eligibility',
    gradient: 'from-lime-500 to-green-600',
    description: 'Collateral-free micro-finance loans for non-corporate, non-farm small/micro enterprises under Shishu, Kishore & Tarun categories.',
    ministry: 'Ministry of Finance',
  },
  {
    id: 'standup-india',
    title: 'Stand-Up India',
    category: 'Entrepreneurship',
    payout: '₹10 L – ₹1 Cr loan',
    status: 'Check Eligibility',
    gradient: 'from-fuchsia-500 to-pink-600',
    description: 'Bank loans between ₹10 lakh and ₹1 crore to at least one SC/ST borrower and one woman borrower per bank branch for greenfield enterprises.',
    ministry: 'Ministry of Finance',
  },
  {
    id: 'naps',
    title: 'National Apprenticeship Promotion',
    category: 'Skill Development',
    payout: '₹1,500/month stipend share',
    status: 'Check Eligibility',
    gradient: 'from-orange-500 to-amber-600',
    description: 'Government shares 25% of prescribed stipend with employers who engage apprentices under the Apprentices Act.',
    ministry: 'Ministry of Skill Development',
  },
  {
    id: 'pm-fasal-bima',
    title: 'PM Fasal Bima Yojana',
    category: 'Agriculture',
    payout: 'Crop loss coverage',
    status: 'Check Eligibility',
    gradient: 'from-emerald-500 to-green-600',
    description: 'Comprehensive crop insurance to provide financial support to farmers suffering crop loss due to unforeseen calamities.',
    ministry: 'Ministry of Agriculture',
  },
  {
    id: 'sukanya-samriddhi',
    title: 'Sukanya Samriddhi Yojana',
    category: 'Girl Child',
    payout: '8.2% p.a. interest',
    status: 'Eligible',
    gradient: 'from-pink-500 to-rose-600',
    description: 'Small savings scheme for girl child with high interest rate and tax benefits, ensuring future education and marriage expenses.',
    ministry: 'Ministry of Finance',
  },
  {
    id: 'nps',
    title: 'National Pension System',
    category: 'Pension',
    payout: 'Market-linked returns',
    status: 'Eligible',
    gradient: 'from-slate-500 to-slate-700',
    description: 'Voluntary, defined contribution retirement savings scheme with tax benefits up to ₹50,000 additionally under Section 80CCD(1B).',
    ministry: 'Ministry of Finance',
  },
  {
    id: 'atal-pension',
    title: 'Atal Pension Yojana',
    category: 'Pension',
    payout: '₹1K–₹5K/month',
    status: 'Check Eligibility',
    gradient: 'from-blue-500 to-indigo-600',
    description: 'Guaranteed minimum pension of ₹1,000 to ₹5,000 per month for unorganised sector workers after age 60.',
    ministry: 'Ministry of Finance',
  },
  {
    id: 'ujjwala',
    title: 'PM Ujjwala Yojana',
    category: 'Energy',
    payout: 'Free LPG connection',
    status: 'Check Eligibility',
    gradient: 'from-yellow-500 to-orange-500',
    description: 'Free LPG connections to women from BPL households to provide clean cooking fuel and empower rural women.',
    ministry: 'Ministry of Petroleum',
  },
]

export default function SchemesPage() {
  const navigate = useNavigate()
  const [savedIds, setSavedIds] = useState(new Set())

  const handleToggleSave = id => setSavedIds(prev => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n })

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 pt-24 pb-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-teal-500/10 border border-teal-500/20 mb-6 shadow-lg shadow-teal-500/10">
              <LayoutGrid className="w-7 h-7 text-teal-400" />
            </div>
            <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-5 tracking-tight">Government Schemes</h1>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
              Explore popular welfare schemes, check your eligibility status, and bookmark them to track your application.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {DISCOVERABLE_SCHEMES.map((scheme) => {
              const isSaved = savedIds.has(scheme.id)
              return (
                <div
                  key={scheme.id}
                  className="rounded-2xl border border-white/[0.07] bg-slate-900/60 backdrop-blur-md overflow-hidden hover:border-white/[0.15] transition-all hover:-translate-y-1 hover:shadow-2xl hover:shadow-teal-500/10 group flex flex-col"
                >
                  <div className={`h-1.5 bg-gradient-to-r ${scheme.gradient}`} />
                  <div className="p-6 flex-1 flex flex-col">
                    <div className="flex items-start gap-4 mb-4">
                      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${scheme.gradient} flex items-center justify-center flex-shrink-0 shadow-lg`}>
                        <IndianRupee className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <div className="min-w-0">
                            <h3 className="text-[16px] font-bold text-white leading-tight">{scheme.title}</h3>
                            <p className="text-[12px] text-slate-500 mt-1">{scheme.ministry}</p>
                          </div>
                          <button
                            onClick={() => handleToggleSave(scheme.id)}
                            className={`flex-shrink-0 w-8 h-8 rounded-xl flex items-center justify-center border transition-all ${
                              isSaved
                                ? 'bg-teal-500/20 border-teal-500/40 text-teal-400'
                                : 'bg-slate-800/60 border-white/[0.07] text-slate-500 hover:text-teal-400 hover:border-teal-500/30'
                            }`}
                          >
                            {isSaved ? <BookmarkCheck className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
                          </button>
                        </div>
                      </div>
                    </div>
                    
                    <p className="text-[13px] text-slate-400 leading-relaxed mb-6 flex-1">{scheme.description}</p>
                    
                    <div className="flex items-center gap-2 flex-wrap mt-auto">
                      <span className="text-[11px] font-semibold text-white bg-teal-500/15 border border-teal-500/25 px-2.5 py-1 rounded-full">{scheme.payout}</span>
                      <span className={`text-[11px] font-semibold px-2.5 py-1 rounded-full border ${
                        scheme.status === 'Eligible'
                          ? 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20'
                          : 'text-amber-400 bg-amber-400/10 border-amber-400/20'
                      }`}>{scheme.status}</span>
                      <span className="text-[11px] text-slate-600 bg-slate-800/60 border border-white/[0.06] px-2.5 py-1 rounded-full">{scheme.category}</span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          <div className="mt-16 text-center">
            <button onClick={() => navigate('/voice')} className="inline-flex items-center justify-center gap-2 px-8 py-3.5 rounded-full bg-slate-900 border border-teal-500/30 text-teal-400 font-semibold hover:bg-teal-500/10 hover:border-teal-500/50 hover:scale-105 transition-all shadow-xl shadow-teal-500/10">
              <Mic className="w-4.5 h-4.5" /> Ask YojVani for more schemes
            </button>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  )
}
