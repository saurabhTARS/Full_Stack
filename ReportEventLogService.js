import axios from 'axios';
import { BASE_URL } from '../consts';
import { getJwtToken } from './AuthenticationService';


//function to get all event logs
export const getAllEventLogReportDataService = () => {
    const lineId = sessionStorage.getItem('lineId');
    console.log(lineId);
    return axios.get(`${BASE_URL}/ReportEventLog/view`, {
        headers: {
            Authorization: `Bearer ${getJwtToken()}`,
            lineId: lineId
          },
    })
        .then(
            (response) => {
                return response.data;
            })
        .catch(
            (error) => {
                throw new Error('Data not loaded');
            })
}

//function to get all event logs filtered by date
export const getAllEventLogReportDataServiceByDate = (serviceParamsData) => {
    const lineId = sessionStorage.getItem('lineId');
    return axios.post(`${BASE_URL}/ReportEventLog/FilterDataByDate`,{
        fromDate: String(serviceParamsData.fromDate),
        toDate: String(serviceParamsData.toDate)
    }, {
        headers: {
            Authorization: `Bearer ${getJwtToken()}`,
            lineId: lineId
          },
    })
        .then(
            (response) => {
                return response.data;
            })
        .catch(
            (error) => {
                throw new Error('Data not loaded');
            })
}