import axios from 'axios';
import type { AnalysisResponse, AnalyzeRequest, Property, PropertyBrief } from '../types';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

// Property endpoints
export async function searchProperties(query: string): Promise<PropertyBrief[]> {
  const { data } = await api.get('/properties/search', { params: { q: query } });
  return data;
}

export async function filterProperties(filters: Record<string, unknown>): Promise<PropertyBrief[]> {
  const { data } = await api.get('/properties/filter', { params: filters });
  return data;
}

export async function getNearbyProperties(
  lat: number,
  lng: number,
  radiusKm = 1.0,
): Promise<PropertyBrief[]> {
  const { data } = await api.get('/properties/nearby', {
    params: { lat, lng, radius_km: radiusKm },
  });
  return data;
}

export async function getProperty(id: string): Promise<Property> {
  const { data } = await api.get(`/properties/${id}`);
  return data;
}

export async function getPropertyByParcel(parcelId: string): Promise<Property> {
  const { data } = await api.get(`/properties/parcel/${parcelId}`);
  return data;
}

// Analysis endpoint
export async function analyzeProperty(request: AnalyzeRequest): Promise<AnalysisResponse> {
  const { data } = await api.post('/analyze-property', request);
  return data;
}

// Scenario endpoints
export async function getPropertyScenarios(propertyId: string) {
  const { data } = await api.get(`/scenarios/property/${propertyId}`);
  return data;
}

export async function getScenarioDetail(scenarioId: string) {
  const { data } = await api.get(`/scenarios/${scenarioId}`);
  return data;
}

export async function compareScenarios(scenarioIds: string[]) {
  const { data } = await api.post('/scenarios/compare', null, {
    params: { scenario_ids: scenarioIds },
  });
  return data;
}

export async function setPreferredScenario(scenarioId: string) {
  const { data } = await api.patch(`/scenarios/${scenarioId}/prefer`);
  return data;
}

// Report endpoints
export async function downloadReport(propertyId: string): Promise<Blob> {
  const { data } = await api.get(`/reports/property/${propertyId}/pdf`, {
    responseType: 'blob',
  });
  return data;
}

export default api;
