export interface Property {
  id: string;
  parcel_id: string;
  address: string;
  city: string;
  province: string;
  postal_code: string | null;
  lot_width_ft: number | null;
  lot_depth_ft: number | null;
  lot_area_sqft: number | null;
  current_use: string | null;
  structure_type: string | null;
  year_built: number | null;
  num_storeys: number | null;
  gross_floor_area_sqft: number | null;
  num_units: number | null;
  assessed_value: number | null;
  assessed_land_value: number | null;
  assessed_building_value: number | null;
  zoning_code: string | null;
  zoning_description: string | null;
  ward: string | null;
  neighbourhood: string | null;
  is_heritage: boolean;
  is_floodplain: boolean;
  has_easements: boolean;
  opportunity_score: number | null;
  risk_factors: Record<string, unknown> | null;
  last_updated: string;
}

export interface PropertyBrief {
  id: string;
  parcel_id: string;
  address: string;
  zoning_code: string | null;
  lot_area_sqft: number | null;
  assessed_value: number | null;
  opportunity_score: number | null;
}

export interface CostBreakdown {
  acquisition: number;
  teardown: number;
  hard_construction: number;
  soft_costs: number;
  development_charges: number;
  permit_fees: number;
  financing: number;
  hst: number;
  total: number;
}

export interface ROIMetrics {
  profit: number;
  profit_margin_pct: number;
  roi_pct: number;
  irr_pct: number | null;
  cap_rate_pct: number | null;
  cash_on_cash_pct: number | null;
}

export interface SensitivityResult {
  variable: string;
  base_value: number;
  low_case: number;
  high_case: number;
  impact_on_roi_pct: number;
}

export interface Scenario {
  id?: string;
  scenario_type: string;
  title: string;
  description: string;
  target_use: string;
  proposed_units: number | null;
  proposed_storeys: number | null;
  proposed_gfa_sqft: number | null;
  costs: CostBreakdown;
  projected_sale_revenue: number | null;
  projected_annual_rental: number | null;
  roi_metrics: ROIMetrics;
  timeline_months: number;
  risks: string[];
  opportunity_score: number;
  confidence_level: string;
  sensitivity_analysis: SensitivityResult[] | null;
}

export interface AnalysisResponse {
  property_id: string;
  address: string;
  parcel_id: string;
  zoning_code: string;
  zoning_summary: string;
  lot_area_sqft: number;
  overall_opportunity_score: number;
  scenarios: Scenario[];
  disclaimer: string;
  generated_at: string;
}

export interface AnalyzeRequest {
  address?: string;
  parcel_id?: string;
  acquisition_cost?: number;
  target_use: string;
}

export type MapLayer = 'zoning' | 'parcels' | 'floodplain' | 'heritage';

export type TabId = 'overview' | 'zoning' | 'costs' | 'scenarios';
