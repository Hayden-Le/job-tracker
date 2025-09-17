import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import { promises as fs } from 'fs';
import path from 'path';

export async function POST(req: NextRequest) {
  const formData = await req.formData();
  const file = formData.get('cv') as File;

  if (!file) {
    return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
  }

  const bytes = await file.arrayBuffer();
  const buffer = Buffer.from(bytes);

  // Ensure the uploads directory exists and save the file
  const uploadDir = path.join(process.cwd(), 'uploads');
  await fs.mkdir(uploadDir, { recursive: true });
  const uploadPath = path.join(uploadDir, file.name);
  await fs.writeFile(uploadPath, buffer);

  // The Python script is in the parent directory, under `backend`
  const pythonScript = path.join(process.cwd(), '..', 'backend', 'cv_to_keywords.py');
  
  // We need to run python from the root of the project for imports to work
  const projectRoot = path.join(process.cwd(), '..');

  console.log(`Running script: ${pythonScript} with file: ${file.name}`);

  const pythonProcess = spawn('python', ['-m', 'backend.cv_to_keywords', file.name], { 
    cwd: projectRoot,
    env: { ...process.env, PYTHONPATH: projectRoot },
  });

  let output = '';
  let error = '';
  pythonProcess.stdout.on('data', (data) => { output += data.toString(); console.log('PY_STDOUT:', data.toString()); });
  pythonProcess.stderr.on('data', (data) => { error += data.toString(); console.error('PY_STDERR:', data.toString()); });

  const exitCode: number = await new Promise((resolve) => {
    pythonProcess.on('close', resolve);
  });

  if (exitCode !== 0) {
    return NextResponse.json({ success: false, error: `Python script failed with code ${exitCode}: ${error}` }, { status: 500 });
  }

  try {
    // The python script should output a single line of JSON
    const result = JSON.parse(output);
    return NextResponse.json(result);
  } catch (e) {
    return NextResponse.json({ success: false, error: 'Failed to parse Python script output.', details: output }, { status: 500 });
  }
}
