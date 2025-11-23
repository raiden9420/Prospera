import React from 'react';
import { Chart } from 'react-google-charts';

interface ChartRendererProps {
    chartType: string;
    data: any[];
    options: any;
    width?: string;
    height?: string;
}

export const ChartRenderer: React.FC<ChartRendererProps> = ({
    chartType,
    data,
    options,
    width = "100%",
    height = "400px"
}) => {
    return (
        <div className="w-full h-full bg-white rounded-lg shadow-sm p-4 border border-gray-200">
            <Chart
                chartType={chartType as any}
                width={width}
                height={height}
                data={data}
                options={{
                    ...options,
                    backgroundColor: 'transparent',
                    chartArea: { width: '80%', height: '70%' },
                }}
                loader={<div className="flex justify-center items-center h-full text-gray-500">Loading Chart...</div>}
            />
        </div>
    );
};
