/*

Neural Network on Predicting the Cumulative P&L of JPM

Group Member: Xiaolin Shen, Yi Wen, Shu Xie


*/
#include<iostream>
#include<fstream>
#include<stdlib.h>
#include<stdio.h>
#include<math.h>
#include<algorithm>
#include<vector>
#include<ctime>
#include<iomanip>

using namespace std;

#define	FALSE	0
#define TRUE	1
#define	NOT	!
#define	AND	&&
#define OR	||
#define MIN_DOUBLE	-HUGE_VAL
#define MAX_DOUBLE	+HUGE_VAL
#define LO	0.001
#define HI	0.999
#define BIAS	1
#define sqr(x)	x*x

typedef struct{			/* A LAYER OF A NET:                     */
	int	units;			/* - number of units in this layer       */
	double*	Output;		/* - output of ith unit                  */
	double*	Error;		/* - error term of ith unit              */
	double** Weight;		/* - connection weights to ith unit      */
	double** WeightSave;	/* - saved weights for stopped training  */
	double** dWeight;	/* - last weight deltas for momentum     */
}LAYER;

typedef struct {           /* A NET:                                */
	LAYER**	Layer;         /* - layers of this net                  */
	LAYER*	InputLayer;    /* - input layer                         */
	LAYER*	OutputLayer;   /* - output layer                        */
	double	Alpha;         /* - momentum factor                     */
	double	Eta;           /* - learning rate                       */
	double	Gain;          /* - gain of sigmoid function            */
	double	Error;         /* - total net error                     */
}NET;


void InitializeRandoms()
{
	srand(time(0));
}

int RandomEqualINT(int Low, int High)
{
	return rand() % (High - Low + 1) + Low;
}

double RandomEqualdouble(double Low, double High)
{
	return ((double)rand() / RAND_MAX) * (High - Low) + Low;
}


#define NUM_LAYERS	3
#define N	5
#define M	1
int	Units[NUM_LAYERS] = { N, 10, M };

#define FIRST_DAY	1
#define NUM_DAYS	200

#define TRAIN_LWB	1
#define TRAIN_UPB	99	// Data from row 2 to row 100 are used to train the network
#define TRAIN_DAYS	(TRAIN_UPB - TRAIN_LWB + 1)
#define TEST_LWB	100
#define TEST_UPB	179	// Data from row 101 to 180 are used for testing
#define TEST_DAYS	(TEST_UPB - TEST_LWB + 1)
#define EVAL_LWB	180    
#define EVAL_UPB    (NUM_DAYS - 1)  // The rest 20 data is used as evaluation.
#define EVAL_DAYS	(EVAL_UPB - EVAL_LWB + 1)

double Raw[NUM_DAYS][5] = { 0.0 };
double Diff[NUM_DAYS][5] = { 0.0 };
double Nor[NUM_DAYS][5] = { 0.0 };

double Simulate[EVAL_DAYS][1] = { 0.0 };
double Mean; // mean of the stock daily return, the first column
double TrainError;
double TrainErrorPredictingMean;
double TestError;
double TestErrorPredictingMean;

fstream file;
ifstream load;
ofstream write1;
ofstream write2;

// normalize all the economic data and get the mean
// Here we have five different variables
void Normalization()
{
	for (int i = 0; i < 5; i++)
	{
		vector<double> dvec;
		// get the differential form
		for (int DAY = 0; DAY < NUM_DAYS - 1; DAY++)
		{
			//Diff[DAY+1][i] = (Raw[DAY+1][i] - Raw[DAY][i])/(Raw[DAY+1][i] + Raw[DAY][i]);
			Diff[DAY + 1][i] = Raw[DAY + 1][i] - Raw[DAY][i];
			dvec.push_back(Diff[DAY + 1][i]);
		}
		// get the normalized form
		double max = 0.0;
		double min = 0.0;
		sort(dvec.begin(), dvec.end()); // ascending order
		max = dvec.back();
		min = dvec[0];
		vector<double>(dvec).swap(dvec); // release the memory
		for (int DAY = 1; DAY < NUM_DAYS; DAY++)
		{
			//Nor[DAY][i] = 2*(Diff[DAY][i]-min)/(max-min)-1;
			Nor[DAY][i] = (Diff[DAY][i] - min) / (max - min);
		}
	}
	double sum = 0.0;
	for (int DAY = 1; DAY < NUM_DAYS; DAY++)
	{
		sum += Nor[DAY][0];
	}
	Mean = sum / (NUM_DAYS - 1);
}

void InitializeApplication(NET* Net)
{
	int	DAY, i;
	double Err;
	Net->Alpha = 0.5;
	Net->Eta = 0.05;
	Net->Gain = 1;

	Normalization();
	TrainErrorPredictingMean = 0;
	for (DAY = TRAIN_LWB; DAY <= TRAIN_UPB; DAY++)
	{
		Err = Mean - Nor[DAY][0];
		TrainErrorPredictingMean += 0.5 * sqr(Err);
	}
	TestErrorPredictingMean = 0;
	for (DAY = TEST_LWB; DAY <= TEST_UPB; DAY++)
	{
		Err = Mean - Nor[DAY][0];
		TestErrorPredictingMean += 0.5 * sqr(Err);
	}
	file.open("Output.txt", std::ios::out);
}

void FinalizeApplication(NET* Net)
{
	file.close();
}

//Initialize the Data

void GenerateNetwork(NET* Net)
{
	int l, i;
	Net->Layer = (LAYER**)calloc(NUM_LAYERS, sizeof(LAYER*));
	for (l = 0; l < NUM_LAYERS; l++)
	{
		Net->Layer[l] = (LAYER*)malloc(sizeof(LAYER));
		Net->Layer[l]->units = Units[l];
		Net->Layer[l]->Output = (double*)calloc(Units[l] + 1, sizeof(double));
		Net->Layer[l]->Error = (double*)calloc(Units[l] + 1, sizeof(double));
		Net->Layer[l]->Weight = (double**)calloc(Units[l] + 1, sizeof(double*));
		Net->Layer[l]->WeightSave = (double**)calloc(Units[l] + 1, sizeof(double*));
		Net->Layer[l]->dWeight = (double**)calloc(Units[l] + 1, sizeof(double*));
		Net->Layer[l]->Output[0] = BIAS;

		if (l != 0)
		{
			for (i = 1; i <= Units[l]; i++)
			{
				Net->Layer[l]->Weight[i] = (double*)calloc(Units[l - 1] + 1, sizeof(double));
				Net->Layer[l]->WeightSave[i] = (double*)calloc(Units[l - 1] + 1, sizeof(double));
				Net->Layer[l]->dWeight[i] = (double*)calloc(Units[l - 1] + 1, sizeof(double));
			}
		}
	}
	Net->InputLayer = Net->Layer[0];
	Net->OutputLayer = Net->Layer[NUM_LAYERS - 1];
	Net->Alpha = 0.9;
	Net->Eta = 0.25;
	Net->Gain = 1;
}

void RandomWeights(NET* Net)
{
	int l, i, j;
	for (l = 1; l < NUM_LAYERS; l++)
	{
		for (i = 1; i <= Net->Layer[l]->units; i++)
		{
			for (j = 0; j <= Net->Layer[l - 1]->units; j++)
			{
				Net->Layer[l]->Weight[i][j] = RandomEqualdouble(-0.5, 0.5);
			}
		}
	}
}

void SetInput(NET* Net, double* Input)
{
	int i;
	for (i = 1; i <= Net->InputLayer->units; i++)
	{
		Net->InputLayer->Output[i] = Input[i - 1];
	}
}

void GetOutput(NET* Net, double* Output)
{
	int i;
	for (i = 1; i <= Net->OutputLayer->units; i++)
	{
		Output[i - 1] = Net->OutputLayer->Output[i];
	}
}

//Decision on when to stop the training

void SaveWeights(NET* Net)
{
	int l, i, j;
	for (l = 1; l < NUM_LAYERS; l++)
	{
		for (i = 1; i <= Net->Layer[l]->units; i++)
		{
			for (j = 0; j <= Net->Layer[l - 1]->units; j++)
			{
				Net->Layer[l]->WeightSave[i][j] = Net->Layer[l]->Weight[i][j];
				if (l == 1)
					write1 << "Hidden Layer " << " Node " << i << " Weight " << j << ": " << Net->Layer[l]->Weight[i][j] << std::endl;
				else
					write1 << "Output Layer " << " Node " << i << " Weight " << j << ": " << Net->Layer[l]->Weight[i][j] << std::endl;
			}
		}
	}
}

void RestoreWeights(NET* Net)
{
	int l, i, j;
	for (l = 1; l < NUM_LAYERS; l++)
	{
		for (i = 1; i <= Net->Layer[l]->units; i++)
		{
			for (j = 0; j <= Net->Layer[l - 1]->units; j++)
			{
				Net->Layer[l]->Weight[i][j] = Net->Layer[l]->WeightSave[i][j];
			}
		}
	}
}

//How the signal of each node propagate to the next layer

void PropagateLayer(NET* Net, LAYER* Lower, LAYER* Upper)
{
	int i, j;
	double Sum;
	for (i = 1; i <= Upper->units; i++)
	{
		Sum = 0;
		for (j = 0; j <= Lower->units; j++)
		{
			// summation of input node signals
			Sum += Upper->Weight[i][j] * Lower->Output[j];
		}
		Upper->Output[i] = 1 / (1 + exp(-Net->Gain * Sum));
		//Upper->Output[i] = 2/(1 + exp(-Net->Gain * Sum)) - 1;
	}
}

void PropagateNet(NET* Net)
{
	int l;
	for (l = 0; l < NUM_LAYERS - 1; l++)
	{
		PropagateLayer(Net, Net->Layer[l], Net->Layer[l + 1]);
	}
}


void ComputeOutputError(NET* Net, double* Target)
{
	int i;
	double Out, Err;
	Net->Error = 0;
	for (i = 1; i <= Net->OutputLayer->units; i++)
	{
		Out = Net->OutputLayer->Output[i];
		Err = Target[i - 1] - Out;
		Net->OutputLayer->Error[i] = Net->Gain * Out * (1 - Out) * Err;
		//Net->OutputLayer->Error[i] = Net->Gain * (1 + Out) * (1 - Out) * Err * 0.5;
		Net->Error += 0.5 * sqr(Err);
	}
}

void BackpropagateLayer(NET* Net, LAYER* Upper, LAYER* Lower)
{
	int i, j;
	double Out, Err;
	for (i = 1; i <= Lower->units; i++)
	{
		Out = Lower->Output[i];
		Err = 0;
		for (j = 1; j <= Upper->units; j++)
		{
			Err += Upper->Weight[j][i] * Upper->Error[j];
		}
		Lower->Error[i] = Net->Gain * Out * (1 - Out) * Err;
		//Lower->Error[i] = Net->Gain * (1 + Out) * (1 - Out) * Err * 0.5;
	}
}

void BackpropagateNet(NET* Net)
{
	int l;
	for (l = NUM_LAYERS - 1; l>1; l--)
	{
		BackpropagateLayer(Net, Net->Layer[l], Net->Layer[l - 1]);
	}
}

void AdjustWeights(NET* Net)
{
	int l, i, j;
	double Out, Err, dWeight;
	for (l = 1; l < NUM_LAYERS; l++)
	{
		for (i = 1; i <= Net->Layer[l]->units; i++)
		{
			for (j = 0; j <= Net->Layer[l - 1]->units; j++)
			{
				Out = Net->Layer[l - 1]->Output[j];
				Err = Net->Layer[l]->Error[i];
				dWeight = Net->Layer[l]->dWeight[i][j];
				Net->Layer[l]->Weight[i][j] += Net->Eta * Err * Out + Net->Alpha * dWeight;
				Net->Layer[l]->dWeight[i][j] = Net->Eta * Err * Out;
			}
		}
	}
}

//Simulate the NET

void SimulateNet(NET* Net, double* Input, double* Output, double* Target, bool Training)
{
	SetInput(Net, Input);
	PropagateNet(Net);
	GetOutput(Net, Output);
	ComputeOutputError(Net, Target);
	if (Training)
	{
		BackpropagateNet(Net);
		AdjustWeights(Net);
	}
}

void TrainNet(NET* Net, int Epochs)
{
	int DAY, n;
	double Output[M];
	for (n = 0; n < Epochs*TRAIN_DAYS; n++)
	{
		DAY = RandomEqualINT(TRAIN_LWB, TRAIN_UPB);
		SimulateNet(Net, Nor[DAY - 1], Output, Nor[DAY], TRUE);

	}
}

void TestNet(NET* Net)
{
	int DAY;
	double Output[M];

	TrainError = 0;
	for (DAY = TRAIN_LWB; DAY <= TRAIN_UPB; DAY++)
	{
		SimulateNet(Net, Nor[DAY - 1], Output, Nor[DAY], FALSE);
		TrainError += Net->Error;
	}
	TestError = 0;
	for (DAY = TEST_LWB; DAY <= TEST_UPB; DAY++)
	{
		SimulateNet(Net, Nor[DAY - 1], Output, Nor[DAY], FALSE);
		TestError += Net->Error;
	}

	write2 << "\nNMSE is " << TrainError / TrainErrorPredictingMean << " on Training Set and "
		<< TestError / TestErrorPredictingMean << " on Test Set";
	std::cout << "\nNMSE is " << TrainError / TrainErrorPredictingMean << " on Training Set and "
		<< TestError / TestErrorPredictingMean << " on Test Set";
}

void EvaluateNet(NET* Net)
{
	int DAY;
	double Output[M];

	write2 << "\n\n\n";
	write2 << "DAY		Original		Simulated\n";
	write2 << "\n";

	cout << "\n\n\n";
	cout << "DAY		Original		Simulated\n";
	cout << "\n";

	for (DAY = EVAL_LWB; DAY <= EVAL_UPB; DAY++) {
		SimulateNet(Net, Nor[DAY - 1], Output, Nor[DAY], FALSE);
		Simulate[DAY][0] = Output[0];

		write2 << FIRST_DAY + DAY << "		" << fixed << setw(4) << Nor[DAY][0] << "		" << fixed << setw(4) << Simulate[DAY][0] << endl;
		cout << FIRST_DAY + DAY << "		" << fixed << setw(4) << Nor[DAY][0] << "		" << fixed << setw(4) << Simulate[DAY][0] << endl;
	}
}

//Main Function

int  main()
{
	NET  Net;
	bool Stop;
	double MinTestError;

	write1.open("Weights_Saved.txt");
	write2.open("Output.txt");
	load.open("Input.txt");
	// load in all the raw data
	for (int i = 0; i < NUM_DAYS * 5; i++)
	{
		load >> Raw[i / 5][i % 5];
	}

	InitializeRandoms();
	GenerateNetwork(&Net);
	RandomWeights(&Net);
	InitializeApplication(&Net);

	Stop = FALSE;
	MinTestError = MAX_DOUBLE;
	do{
		TrainNet(&Net, 10);
		TestNet(&Net);
		if (TestError < MinTestError)
		{
			write2 << " - saving Weights ...";
			std::cout << " - saving Weights ...";
			MinTestError = TestError;
			SaveWeights(&Net);
		}
		else if (TestError > 1.2 * MinTestError) {
			write2 << " - stopping Training and restoring Weights ...";
			std::cout << " - stopping Training and restoring Weights ...";
			Stop = TRUE;
			RestoreWeights(&Net);
		}
	} while (NOT Stop);

	TestNet(&Net);
	EvaluateNet(&Net);

	FinalizeApplication(&Net);

	getchar();
}
