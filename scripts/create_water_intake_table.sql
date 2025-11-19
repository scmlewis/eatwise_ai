-- Create water_intake table for tracking daily water consumption
CREATE TABLE IF NOT EXISTS public.water_intake (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    glasses INTEGER NOT NULL DEFAULT 1,
    logged_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, logged_date)
);

-- Enable Row Level Security
ALTER TABLE public.water_intake ENABLE ROW LEVEL SECURITY;

-- Create policy to allow users to view their own water intake
CREATE POLICY "Users can view their own water intake"
    ON public.water_intake FOR SELECT
    USING (auth.uid() = user_id);

-- Create policy to allow users to insert their own water intake
CREATE POLICY "Users can insert their own water intake"
    ON public.water_intake FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Create policy to allow users to update their own water intake
CREATE POLICY "Users can update their own water intake"
    ON public.water_intake FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Create policy to allow users to delete their own water intake
CREATE POLICY "Users can delete their own water intake"
    ON public.water_intake FOR DELETE
    USING (auth.uid() = user_id);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_water_intake_user_date ON public.water_intake(user_id, logged_date);
